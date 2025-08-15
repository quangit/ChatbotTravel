#!/usr/bin/env python3
"""
Demo script to test the Travel AI Assistant functionality
"""

import os
import sys
from pathlib import Path
import json

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test if environment variables are set up correctly"""
    print("🔧 Testing Environment Configuration...")
    
    from config import Config
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY', 
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = getattr(Config, var, None)
        if not value or value == f"your_{var.lower()}":
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {'*' * 10}...")  # Hide sensitive info
    
    if missing_vars:
        print(f"  ❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ All required environment variables are set!")
    return True

def test_database_connection():
    """Test ChromaDB connection"""
    print("\n🗄️ Testing ChromaDB Connection...")
    
    try:
        from app.models import ChromaDBManager
        
        db_manager = ChromaDBManager()
        
        # Try to query (might be empty, that's ok)
        results = db_manager.query_documents("test", n_results=1)
        
        print("  ✅ ChromaDB connection successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ ChromaDB connection failed: {e}")
        return False

def test_ai_agent():
    """Test AI Agent functionality"""
    print("\n🤖 Testing AI Agent...")
    
    try:
        from app.ai_agent import TravelAIAgent
        
        agent = TravelAIAgent()
        print("  ✅ AI Agent initialized successfully!")
        
        # Test simple query
        print("  🧪 Testing simple query...")
        response = agent.process_query("Xin chào")
        print(f"  📝 Response preview: {response[:100]}...")
        
        print("  ✅ AI Agent test successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ AI Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_processing():
    """Test document processing functionality"""
    print("\n📄 Testing Document Processing...")
    
    try:
        from app.models import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test with sample file
        sample_file = project_root / "data" / "sample_travel_data.txt"
        
        if sample_file.exists():
            chunks = processor.process_text_file(str(sample_file))
            print(f"  ✅ Processed {len(chunks)} chunks from sample file")
            return True
        else:
            print("  ⚠️ Sample file not found, creating test content...")
            
            # Create test content
            test_content = "Đây là nội dung test cho document processor."
            chunks = processor.text_splitter.split_text(test_content)
            print(f"  ✅ Document processor working, created {len(chunks)} chunks")
            return True
            
    except Exception as e:
        print(f"  ❌ Document processing test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Testing Flask App...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("  ✅ Flask app created successfully!")
            
            # Test routes
            from app.routes import main
            print(f"  ✅ Routes registered: {len(main.deferred_functions)} endpoints")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app test failed: {e}")
        return False

def run_demo():
    """Run all demo tests"""
    print("🎯 Travel AI Assistant - Demo & Testing")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Database", test_database_connection), 
        ("Document Processing", test_document_processing),
        ("Flask App", test_flask_app),
        ("AI Agent", test_ai_agent),  # Test this last as it requires API calls
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Travel AI Assistant is ready to go!")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n🌐 Then visit: http://localhost:5000")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration and try again.")
        print("💡 Make sure your .env file is properly configured with Azure OpenAI credentials.")
    
    return passed == total

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
