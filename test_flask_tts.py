#!/usr/bin/env python3
"""
Test TTS Service Integration
"""

import requests
import json
import base64

def test_flask_tts():
    print("🔄 Testing Flask TTS Integration...")
    
    # Test URL
    url = "http://localhost:5000/tts"
    
    # Test data
    test_cases = [
        "Xin chào! Tôi là trợ lý du lịch AI.",
        "Phở bò là món ăn ngon nhất Việt Nam.",
        "Hà Nội có nhiều địa điểm du lịch hấp dẫn."
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🎯 Test {i}: {text}")
        
        try:
            # Send POST request
            data = {"text": text}
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Save audio
                    audio_data = base64.b64decode(result["audio"])
                    filename = f"flask_test_{i}.wav"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                    print(f"✅ Success! Audio saved to {filename}")
                    print(f"📊 Size: {len(audio_data):,} bytes")
                else:
                    print(f"❌ TTS Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            print("💡 Make sure Flask app is running on port 5000")
            break
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            break
    
    print("\n🎯 Flask TTS Test Completed!")

if __name__ == "__main__":
    test_flask_tts()
