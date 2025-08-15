#!/usr/bin/env python3
"""
Test AI Agent without temperature parameter
"""

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_agent():
    print("🤖 Testing AI Agent without temperature...")
    
    try:
        from app.ai_agent import TravelAIAgent
        
        print("🔧 Initializing AI Agent...")
        agent = TravelAIAgent()
        
        print("✅ AI Agent initialized successfully!")
        
        print("🧪 Testing simple query...")
        response = agent.process_query("Xin chào, bạn có thể giúp tôi tìm hiểu về Hà Nội không?")
        
        print("✅ Query processed successfully!")
        print(f"📝 Response preview: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_agent()
    if success:
        print("\n🎉 AI Agent test completed successfully!")
    else:
        print("\n❌ AI Agent test failed!")
