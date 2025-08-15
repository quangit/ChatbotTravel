#!/usr/bin/env python3
"""
Quick test to verify Flask app can render templates
"""

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_flask_templates():
    print("🧪 Testing Flask template rendering...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            print("🔧 Testing GET / (index page)...")
            response = client.get('/')
            
            if response.status_code == 200:
                print("✅ Index page rendered successfully!")
                print(f"📄 Response length: {len(response.data)} bytes")
                
                # Check if it contains expected content
                html_content = response.data.decode('utf-8')
                if 'Trợ lý Du lịch AI' in html_content:
                    print("✅ Page contains expected title!")
                else:
                    print("⚠️ Page doesn't contain expected title")
                    
            else:
                print(f"❌ Failed to render index page. Status: {response.status_code}")
                print(f"Response: {response.data.decode('utf-8')}")
            
            print("\n🔧 Testing GET /admin (admin login page)...")
            response = client.get('/admin')
            
            if response.status_code == 200:
                print("✅ Admin login page rendered successfully!")
            else:
                print(f"❌ Failed to render admin page. Status: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flask_templates()
