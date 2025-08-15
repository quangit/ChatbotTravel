from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import base64
import requests
from config import Config
from app.models import ChromaDBManager
import re

class AgentState(TypedDict):
    messages: List[str]
    query: str
    query_type: str  # "text" or "image"
    image_data: str
    retrieved_docs: List[str]
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
        
        # Add edges
        workflow.add_edge("analyze_input", "retrieve_docs")
        workflow.add_edge("retrieve_docs", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_input")
        
        return workflow.compile()
    
    def _analyze_input(self, state: AgentState) -> AgentState:
        """Analyze user input to determine query type"""
        if state.get("image_data"):
            # Process image
            try:
                image_analysis = self._analyze_image(state["image_data"])
                state["query"] = image_analysis
                state["query_type"] = "image"
            except Exception as e:
                state["query"] = "Không thể phân tích hình ảnh này"
                state["query_type"] = "text"
        else:
            # Text query
            state["query_type"] = "text"
        
        return state
    
    def _analyze_image(self, image_data: str) -> str:
        """Analyze image using Vision API"""
        try:
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
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = self.vision_llm.invoke(messages)
            return response.content
            
        except Exception as e:
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
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM"""
        try:
            # Prepare context from retrieved documents
            context = "\n".join(state["retrieved_docs"]) if state["retrieved_docs"] else "Không có thông tin liên quan trong cơ sở dữ liệu."
            
            # System message
            system_message = """
            Bạn là một trợ lý du lịch AI chuyên về Việt Nam. Nhiệm vụ của bạn:
            
            1. Trả lời câu hỏi về địa điểm du lịch, món ăn, nhà hàng
            2. Cung cấp thông tin chi tiết, hữu ích và chính xác
            3. Khi đề cập đến nhà hàng/địa điểm, cung cấp địa chỉ cụ thể
            4. Tạo liên kết Google Maps cho các địa điểm (format: [Xem bản đồ](https://maps.google.com/maps?q=TEN_DIA_DIEM))
            5. Trả lời bằng tiếng Việt, thân thiện và nhiệt tình
            
            Thông tin có sẵn:
            """ + context
            
            # User query
            user_message = f"Câu hỏi: {state['query']}"
            
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            state["response"] = response.content
            
            # Add Google Maps links
            state["response"] = self._add_google_maps_links(state["response"])
            
        except Exception as e:
            state["response"] = f"Xin lỗi, tôi đang gặp sự cố kết nối. Vui lòng thử lại sau. Lỗi: {str(e)}"
        
        return state
    
    def _add_google_maps_links(self, text: str) -> str:
        """Add Google Maps links to locations mentioned in the response"""
        # Simple regex to find potential addresses or restaurant names
        # This is a basic implementation, can be improved
        patterns = [
            r'([A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+(?:quán|nhà hàng|chùa|đền|hồ|phố|đường)[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]*)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                maps_url = f"https://maps.google.com/maps?q={location.replace(' ', '+')}"
                replacement = f"{location} [Xem bản đồ]({maps_url})"
                text = text.replace(location, replacement, 1)
        
        return text
    
    def process_query(self, query: str, image_data: str = None) -> str:
        """Process user query and return response"""
        initial_state = {
            "messages": [],
            "query": query,
            "query_type": "text",
            "image_data": image_data,
            "retrieved_docs": [],
            "response": ""
        }
        
        final_state = self.workflow.invoke(initial_state)
        return final_state["response"]
