#!/usr/bin/env python3
"""
Simple test for AzureOpenAI embeddings
"""

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from app.models import ChromaDBManager

def test_embeddings():
    print("🧪 Testing AzureOpenAI embeddings...")
    
    try:
        # Test configuration
        print(f"📍 Embedding Endpoint: {Config.AZURE_OPENAI_EMBEDDING_ENDPOINT}")
        print(f"📅 Embedding API Version: {Config.AZURE_OPENAI_EMBEDDING_API_VERSION}")
        print(f"🚀 Embedding Deployment: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME}")
        
        # Initialize ChromaDB Manager
        print("🔧 Initializing ChromaDB Manager...")
        db_manager = ChromaDBManager()
        
        print("✅ ChromaDB Manager initialized successfully!")
        
        # Test embedding creation
        print("🔍 Testing embedding creation...")
        test_texts = ["Hà Nội là thủ đô của Việt Nam"]
        
        success = db_manager.add_documents(test_texts, [{"source": "test"}])
        
        if success:
            print("✅ Embeddings created and added successfully!")
            
            # Test query
            print("🔍 Testing query...")
            results = db_manager.query_documents("Hà Nội", n_results=1)
            
            if results and results.get("documents"):
                print("✅ Query test successful!")
                print(f"📊 Found {len(results['documents'][0])} results")
                print(f"📄 First result: {results['documents'][0][0][:100]}...")
            else:
                print("⚠️ Query returned no results")
                print(f"Debug - Results: {results}")
                
        else:
            print("❌ Failed to create embeddings")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_embeddings()
