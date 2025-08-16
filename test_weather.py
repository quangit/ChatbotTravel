#!/usr/bin/env python3
"""
Test script for weather functionality in TravelAIAgent
"""

from app.ai_agent import TravelAIAgent
from config import Config
import os

def test_weather_queries():
    """Test various weather-related queries"""
    
    # Check if OpenWeather API key is configured
    if not Config.OPENWEATHER_API_KEY:
        print("❌ OpenWeather API key not configured in .env file")
        print("Please add OPENWEATHER_API_KEY=your_api_key_here to .env")
        return
    
    # Initialize the AI agent
    print("🚀 Initializing TravelAIAgent...")
    agent = TravelAIAgent()
    
    # Test queries
    test_queries = [
        "Thời tiết ở Hà Nội hôm nay như thế nào?",
        "Tôi muốn đi du lịch Đà Nẵng, thời tiết thế nào?",
        "Hồ Chí Minh City có mưa không?",
        "Hội An thời tiết ra sao?",
        "Tôi muốn biết thời tiết ở Sapa",
        "Du lịch Phú Quốc nên mặc gì?"
    ]
    
    print("\n" + "="*60)
    print("🌤️  TESTING WEATHER FUNCTIONALITY")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = agent.process_query(query)
            print(f"✅ Response:\n{response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)

def test_location_extraction():
    """Test location extraction functionality"""
    from app.ai_agent import TravelAIAgent
    
    agent = TravelAIAgent()
    
    test_cases = [
        "Hà Nội là thủ đô của Việt Nam với nhiều di tích lịch sử...",
        "Du lịch Đà Nẵng rất thú vị với bãi biển Mỹ Khê...",
        "Sapa là vùng núi phía Bắc nổi tiếng với ruộng bậc thang...",
        "Phở bò là món ăn truyền thống của Việt Nam...",  # Không có địa điểm cụ thể
    ]
    
    print("\n" + "="*60)
    print("📍 TESTING LOCATION EXTRACTION FROM RESPONSE")
    print("="*60)
    
    for i, response_text in enumerate(test_cases, 1):
        print(f"\n{i}. Response: {response_text}")
        location = agent._extract_location(response_text)
        print(f"   Extracted location: '{location}'")
        print("-" * 50)

if __name__ == "__main__":
    print("🌟 Weather Testing for ChatbotTravel")
    print("="*60)
    
    # Test location extraction first
    test_location_extraction()
    
    # Test full weather queries
    test_weather_queries()
    
    print("\n✅ Testing completed!")
