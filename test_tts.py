#!/usr/bin/env python3
"""
Test script for MMS TTS Vietnamese model
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tts_service import TTSService
import time

def test_tts():
    print("🎤 Testing MMS TTS Vietnamese Model")
    print("=" * 50)
    
    # Initialize TTS service
    print("📥 Initializing TTS Service...")
    start_time = time.time()
    tts = TTSService()
    init_time = time.time() - start_time
    print(f"⏱️ Initialization time: {init_time:.2f}s")
    
    if tts.model is None:
        print("❌ Model failed to load!")
        return
    
    # Test cases
    test_cases = [
        "Xin chào! Tôi là trợ lý du lịch AI.",
        "Phở bò là món ăn truyền thống của Việt Nam.",
        "Hà Nội là thủ đô của Việt Nam với nhiều địa điểm du lịch hấp dẫn.",
        "Bánh mì Việt Nam rất ngon và được yêu thích trên toàn thế giới!"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🔊 Test {i}: {text}")
        print("-" * 40)
        
        start_time = time.time()
        audio_data = tts.text_to_speech(text)
        process_time = time.time() - start_time
        
        if audio_data:
            print(f"✅ Success!")
            print(f"📊 Audio size: {len(audio_data):,} bytes")
            print(f"⏱️ Processing time: {process_time:.2f}s")
            
            # Save audio file for testing
            output_file = f"test_audio_{i}.wav"
            with open(output_file, "wb") as f:
                f.write(audio_data)
            print(f"💾 Saved to: {output_file}")
        else:
            print(f"❌ Failed to generate audio")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_tts()
