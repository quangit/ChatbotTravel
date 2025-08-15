#!/usr/bin/env python3
"""
Script to initialize the ChromaDB database with sample data
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models import ChromaDBManager, DocumentProcessor
from config import Config

def initialize_database():
    """Initialize ChromaDB with sample data"""
    print("🚀 Initializing Travel AI Assistant Database...")
    
    try:
        # Create data directory if it doesn't exist
        os.makedirs(Config.CHROMADB_PATH, exist_ok=True)
        
        # Initialize managers
        db_manager = ChromaDBManager()
        doc_processor = DocumentProcessor()
        
        print("✅ ChromaDB connection established")
        
        # Process sample data file
        sample_file = project_root / "data" / "sample_travel_data.txt"
        
        if sample_file.exists():
            print(f"📄 Processing sample data from {sample_file}")
            
            # Process the text file
            chunks = doc_processor.process_text_file(str(sample_file))
            
            if chunks:
                print(f"📦 Created {len(chunks)} text chunks")
                
                # Create metadata for chunks
                metadatas = [
                    {
                        'source': 'sample_travel_data.txt',
                        'chunk_id': i,
                        'content_type': 'travel_info'
                    }
                    for i in range(len(chunks))
                ]
                
                # Add to database
                success = db_manager.add_documents(chunks, metadatas)
                
                if success:
                    print("✅ Sample data added to ChromaDB successfully!")
                else:
                    print("❌ Failed to add sample data to ChromaDB")
                    return False
            else:
                print("❌ No chunks generated from sample file")
                return False
        else:
            print(f"⚠️ Sample data file not found at {sample_file}")
            print("📝 Creating basic welcome message...")
            
            # Create a basic welcome message
            welcome_chunks = [
                "Chào mừng bạn đến với Trợ lý Du lịch AI! Tôi có thể giúp bạn tìm hiểu về các địa điểm du lịch và món ăn ngon tại Việt Nam.",
                "Bạn có thể hỏi tôi về các thành phố như Hà Nội, Hồ Chí Minh, Đà Nẵng, Hội An, Huế, Đà Lạt và nhiều địa điểm khác.",
                "Tôi cũng có thể giới thiệu về các món ăn đặc sản như phở, bún chả, bánh mì, cơm tấm, bánh cuốn và nhiều món ngon khác."
            ]
            
            metadatas = [
                {
                    'source': 'system_init',
                    'chunk_id': i,
                    'content_type': 'welcome_message'
                }
                for i in range(len(welcome_chunks))
            ]
            
            success = db_manager.add_documents(welcome_chunks, metadatas)
            
            if success:
                print("✅ Basic welcome messages added to ChromaDB!")
            else:
                print("❌ Failed to add welcome messages to ChromaDB")
                return False
        
        # Test query
        print("🔍 Testing database query...")
        results = db_manager.query_documents("Hồ Gươm", n_results=2)
        
        if results and results.get("documents"):
            print(f"✅ Query test successful! Found {len(results['documents'][0])} relevant documents")
        else:
            print("⚠️ Query test returned no results, but database is initialized")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Next steps:")
        print("1. Make sure your .env file is configured with API keys")
        print("2. Run: python app.py")
        print("3. Visit: http://localhost:5000")
        print("4. Upload more documents via admin panel at: http://localhost:5000/admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
