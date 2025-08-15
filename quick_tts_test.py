#!/usr/bin/env python3
"""
Simple TTS test
"""

print("🎤 Testing MMS TTS...")

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    
    import transformers
    print(f"✅ Transformers: {transformers.__version__}")
    
    import soundfile
    print(f"✅ SoundFile available")
    
    print("\n🔄 Loading MMS model...")
    from transformers import VitsModel, VitsTokenizer
    
    model_name = "facebook/mms-tts-vie"
    print(f"📥 Loading tokenizer: {model_name}")
    tokenizer = VitsTokenizer.from_pretrained(model_name)
    
    print(f"📥 Loading model: {model_name}")
    model = VitsModel.from_pretrained(model_name)
    
    print("✅ Model loaded successfully!")
    
    # Quick test
    print("\n🔊 Quick test...")
    text = "Xin chào"
    print(f"Input text: {text}")
    
    inputs = tokenizer(text, return_tensors="pt")
    print("✅ Text tokenized")
    
    with torch.no_grad():
        outputs = model(**inputs)
        audio = outputs.waveform[0].numpy()
    
    print(f"✅ Audio generated: {len(audio)} samples")
    
    # Save test audio
    import soundfile as sf
    import numpy as np
    
    # Ensure audio is in correct format
    if len(audio.shape) == 1:
        audio = audio.reshape(-1, 1)
    
    sf.write("quick_test.wav", audio, 22050)
    print("💾 Saved to: quick_test.wav")
    
    print("\n🎯 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
