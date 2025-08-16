from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import base64
import requests
import json
from config import Config
from app.models import ChromaDBManager
import re

class AgentState(TypedDict):
    messages: List[dict]  # Lưu các messages format cho LangChain
    chat_history: List[dict]  # Lưu lịch sử chat
    query: str
    query_type: str  # "text" or "image"
    image_data: str
    retrieved_docs: List[str]
    location_info: str  # Extracted location for weather
    weather_info: str   # Weather information
    response: str

class TravelAIAgent:
    def __init__(self):
        # Initialize LLM with temperature only if supported
        llm_params = {
            'azure_endpoint': Config.AZURE_OPENAI_ENDPOINT,
            'api_key': Config.AZURE_OPENAI_API_KEY,
            'api_version': Config.AZURE_OPENAI_API_VERSION,
            'azure_deployment': Config.AZURE_OPENAI_DEPLOYMENT_NAME
        }
        
        # Only add temperature if it's not 0.7 (unsupported by GPT-5)
        if Config.AZURE_OPENAI_TEMPERATURE != 0.7:
            llm_params['temperature'] = Config.AZURE_OPENAI_TEMPERATURE
            
        self.llm = AzureChatOpenAI(**llm_params)
        
        # Use same configuration for vision LLM
        self.vision_llm = AzureChatOpenAI(**llm_params)
        
        self.db_manager = ChromaDBManager()
        
        # Build the agent workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("retrieve_docs", self._retrieve_docs)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("get_weather", self._get_weather_info)
        workflow.add_node("final_response", self._generate_final_response)
        
        # Add edges
        workflow.add_edge("analyze_input", "retrieve_docs")
        workflow.add_edge("retrieve_docs", "generate_response")
        workflow.add_edge("generate_response", "get_weather")
        workflow.add_edge("get_weather", "final_response")
        workflow.add_edge("final_response", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_input")
        
        return workflow.compile()
    
    def _analyze_input(self, state: AgentState) -> AgentState:
        """Analyze user input to determine query type"""
        if state.get("image_data"):
            # Process image
            try:
                print(f"[DEBUG] Processing image data, length: {len(state['image_data']) if state['image_data'] else 0}")
                image_analysis = self._analyze_image(state["image_data"])
                state["query"] = image_analysis
                state["query_type"] = "image"
                print(f"[DEBUG] Image analysis result: {image_analysis[:100]}...")
            except Exception as e:
                print(f"[ERROR] Image analysis failed: {str(e)}")
                import traceback
                traceback.print_exc()
                state["query"] = "Không thể phân tích hình ảnh này"
                state["query_type"] = "text"
        else:
            # Text query
            state["query_type"] = "text"
        
        return state
    
    def _analyze_image(self, image_data: str) -> str:
        """Analyze image using Vision API"""
        try:
            print("[DEBUG] Starting image analysis...")
            
            # Validate image data
            if not image_data or len(image_data.strip()) == 0:
                return "Dữ liệu hình ảnh không hợp lệ"
            
            # Prepare messages for vision model
            messages = [
                SystemMessage(content="""
                Bạn là một chuyên gia du lịch Việt Nam. Hãy phân tích hình ảnh này và xác định:
                1. Nếu là món ăn: Tên món ăn và mô tả ngắn gọn
                2. Nếu là địa điểm: Tên địa điểm và vị trí
                3. Trả lời bằng tiếng Việt, ngắn gọn và chính xác
                """),
                HumanMessage(content=[
                    {"type": "text", "text": "Hình ảnh này là gì?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}", "detail": "low"}}
                ])
            ]
            
            print("[DEBUG] Calling vision LLM...")
            response = self.vision_llm.invoke(messages)
            result = response.content
            print(f"[DEBUG] Vision LLM response: {result[:100]}...")
            return result
            
        except Exception as e:
            print(f"[ERROR] Image analysis error: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Không thể phân tích hình ảnh: {str(e)}"
    
    def _retrieve_docs(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from ChromaDB"""
        try:
            results = self.db_manager.query_documents(state["query"], n_results=3)
            
            if results and results.get("documents"):
                state["retrieved_docs"] = results["documents"][0]  # First result list
            else:
                state["retrieved_docs"] = []
                
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            state["retrieved_docs"] = []
        
        return state
        
    def _update_chat_history(self, state: AgentState, query: str, response: str) -> List[dict]:
        """Cập nhật lịch sử chat"""
        if "chat_history" not in state:
            state["chat_history"] = []
        
        # Thêm tin nhắn mới
        state["chat_history"].extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ])
        
        # Giới hạn lịch sử (giữ 10 lượt gần nhất)
        max_turns = 10
        if len(state["chat_history"]) > max_turns * 2:
            state["chat_history"] = state["chat_history"][-max_turns * 2:]
        
        return state["chat_history"]
    
    def _extract_location(self, response_text: str) -> str:
        """Extract location name from LLM response"""
        try:
            # Use LLM to extract location from the generated response
            messages = [
                SystemMessage(content="""
                Hãy trích xuất tên thành phố hoặc địa điểm du lịch chính từ văn bản phản hồi sau.
                Chỉ trả về TÊN MỘT địa điểm/thành phố bằng tiếng Anh (ví dụ: Ho Chi Minh City, Hanoi, Da Nang, Hoi An, Sapa, Phu Quoc).
                Nếu có nhiều địa điểm, chọn địa điểm chính được đề cập nhiều nhất.
                Nếu không tìm thấy địa điểm cụ thể, trả về "".
                Chỉ trả về tên địa điểm, không giải thích thêm.
                
                Ví dụ:
                - Input: "Hà Nội là thủ đô..." → Output: "Hanoi"  
                - Input: "Du lịch Đà Nẵng rất thú vị..." → Output: "Da Nang"
                - Input: "Món phở ngon..." → Output: ""
                """),
                HumanMessage(content=f"Phản hồi cần phân tích: {response_text}")
            ]
            
            response = self.llm.invoke(messages)
            location = response.content.strip()
            
            # Clean up the response - remove quotes and extra text
            location = location.replace('"', '').replace("'", '').strip()
            if location.lower() in ['không có', 'không tìm thấy', 'none', 'n/a', '', 'không rõ']:
                return ""
                
            print(f"[DEBUG] Extracted location from response: {location}")
            return location
            
        except Exception as e:
            print(f"[ERROR] Location extraction failed: {str(e)}")
            return ""
    
    def _get_weather_info(self, state: AgentState) -> AgentState:
        """Get weather information for the location mentioned in the response"""
        try:
            # Extract location from the generated response
            location = self._extract_location(state["response"])
            state["location_info"] = location
            
            if not location or not Config.OPENWEATHER_API_KEY:
                state["weather_info"] = ""
                print(f"[DEBUG] Skipping weather - Location: '{location}', API Key available: {bool(Config.OPENWEATHER_API_KEY)}")
                return state
            
            # Get weather data from OpenWeather API
            weather_url = f"{Config.OPENWEATHER_BASE_URL}/weather"
            params = {
                'q': location,
                'appid': Config.OPENWEATHER_API_KEY,
                'units': 'metric',  # Celsius
                'lang': 'vi'  # Vietnamese
            }
            
            response = requests.get(weather_url, params=params, timeout=5)
            
            if response.status_code == 200:
                weather_data = response.json()
                
                # Extract relevant weather information
                weather_info = {
                    'location': weather_data['name'],
                    'country': weather_data['sys']['country'],
                    'temperature': round(weather_data['main']['temp']),
                    'feels_like': round(weather_data['main']['feels_like']),
                    'humidity': weather_data['main']['humidity'],
                    'description': weather_data['weather'][0]['description'],
                    'wind_speed': weather_data.get('wind', {}).get('speed', 0)
                }
                
                # Format weather information in Vietnamese
                weather_text = f"""
🌤️ **Thông tin thời tiết tại {weather_info['location']}, {weather_info['country']}:**
- Nhiệt độ: {weather_info['temperature']}°C (cảm giác như {weather_info['feels_like']}°C)
- Thời tiết: {weather_info['description']}
- Độ ẩm: {weather_info['humidity']}%
- Tốc độ gió: {weather_info['wind_speed']} m/s
"""
                
                state["weather_info"] = weather_text
                print(f"[DEBUG] Weather info retrieved for {location}")
                
            else:
                print(f"[DEBUG] Weather API error: {response.status_code} for location: {location}")
                state["weather_info"] = ""
                
        except Exception as e:
            print(f"[ERROR] Weather info retrieval failed: {str(e)}")
            state["weather_info"] = ""
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate initial response using LLM without weather info"""
        try:
            # Prepare context from retrieved documents
            context = "\n".join(state["retrieved_docs"]) if state["retrieved_docs"] else "Không có thông tin liên quan trong cơ sở dữ liệu."
            
            # System message chỉ chứa context
            system_message = f"""
            Bạn là một trợ lý du lịch AI chuyên về Việt Nam. Nhiệm vụ của bạn:
            
            1. Trả lời câu hỏi về địa điểm du lịch, món ăn, nhà hàng
            2. Cung cấp thông tin chi tiết, hữu ích và chính xác
            3. Khi đề cập đến nhà hàng/địa điểm, cung cấp địa chỉ cụ thể
            4. Tạo liên kết Google Maps cho các địa điểm (format: [Xem bản đồ](https://maps.google.com/maps?q=TEN_DIA_DIEM))
            5. Trả lời bằng tiếng Việt, thân thiện và nhiệt tình
            
            Thông tin có sẵn:
            {context}
            """
            
            # Xây dựng messages array
            state["messages"] = [SystemMessage(content=system_message)]
            
            # Thêm chat history
            if state.get("chat_history"):
                for msg in state["chat_history"]:
                    if msg["role"] == "user":
                        state["messages"].append(HumanMessage(content=msg["content"]))
                    else:
                        state["messages"].append(SystemMessage(content=msg["content"]))
            
            # Thêm câu hỏi hiện tại
            state["messages"].append(HumanMessage(content=state["query"]))
            
            # Gọi LLM
            response = self.llm.invoke(state["messages"])
            state["response"] = response.content
            print(f"[DEBUG] Initial response generated: {state['response'][:100]}...")
            
            # Cập nhật chat history
            self._update_chat_history(state, state["query"], state["response"])
            
        except Exception as e:
            state["response"] = f"Xin lỗi, tôi đang gặp sự cố kết nối. Vui lòng thử lại sau. Lỗi: {str(e)}"
        
        return state
    
    def _generate_final_response(self, state: AgentState) -> AgentState:
        """Generate final response by combining initial response with weather info"""
        try:
            final_response = state["response"]
            
            # Add weather information if available
            if state.get("weather_info"):
                final_response += f"\n\n{state['weather_info']}"
                
                # Add weather-based advice
                weather_advice = self._get_weather_advice(state["weather_info"], state["location_info"])
                if weather_advice:
                    final_response += f"\n💡 **Lời khuyên dựa trên thời tiết:** {weather_advice}"
            
            state["response"] = final_response
            print(f"[DEBUG] Final response with weather info generated")
            
        except Exception as e:
            print(f"[ERROR] Final response generation failed: {str(e)}")
            # Keep the original response if final generation fails
        
        return state
    
    def _get_weather_advice(self, weather_info: str, location: str) -> str:
        """Generate weather-based travel advice"""
        try:
            if not weather_info:
                return ""
            
            messages = [
                SystemMessage(content="""
                Dựa vào thông tin thời tiết được cung cấp, hãy đưa ra lời khuyên ngắn gọn cho du khách về:
                - Trang phục nên mặc
                - Hoạt động phù hợp
                - Lưu ý đặc biệt
                
                Trả lời bằng tiếng Việt, ngắn gọn (2-3 câu), thực tế và hữu ích.
                """),
                HumanMessage(content=f"Thông tin thời tiết: {weather_info}")
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            print(f"[ERROR] Weather advice generation failed: {str(e)}")
            return ""
    
    def _add_google_maps_links(self, text: str) -> str:
        """Replace existing Google Maps links format with proper location names"""
        # Pattern to match existing [Xem bản đồ](https://maps.google.com/maps?q=...) format
        pattern = r'\[Xem bản đồ\]\(https://maps\.google\.com/maps\?q=([^)]+)\)'
        
        def replace_maps_link(match):
            # Extract the location query from the URL
            location_query = match.group(1)
            # Decode URL encoding and replace + with spaces
            location_name = location_query.replace('+', ' ').replace('%20', ' ')
            # Return the formatted link
            return f"[Xem bản đồ](https://maps.google.com/maps?q={location_query})"
        
        # Replace all matches
        result = re.sub(pattern, replace_maps_link, text)
        return result
    
    def process_query(self, query: str, image_data: str = None, chat_history: List[dict] = None) -> str:
        """Process query với chat history"""
        initial_state = {
            "messages": [],
            "chat_history": chat_history or [],
            "query": query,
            "query_type": "text",
            "image_data": image_data,
            "retrieved_docs": [],
            "location_info": "",
            "weather_info": "",
            "response": ""
        }
        
        final_state = self.workflow.invoke(initial_state)
        return final_state
