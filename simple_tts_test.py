import requests
import json

print("Testing TTS endpoint...")

try:
    # Test simple request
    url = "http://127.0.0.1:5000/tts"
    data = {"text": "Xin chào"}
    
    print(f"Sending request to {url}")
    print(f"Data: {data}")
    
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Response keys: {list(result.keys())}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
