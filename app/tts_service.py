import torch
import soundfile as sf
from transformers import VitsModel, VitsTokenizer
import io
import numpy as np
from config import Config
import re

class TTSService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[TTS] Using device: {self.device}")
        
        # Load Vietnamese MMS TTS model and tokenizer
        try:
            print("[TTS] Loading facebook/mms-tts-vie model...")
            self.model = VitsModel.from_pretrained("facebook/mms-tts-vie")
            self.tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-vie")
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            print("[TTS] Model loaded successfully!")
            
        except Exception as e:
            print(f"[TTS ERROR] Failed to load model: {e}")
            self.model = None
            self.tokenizer = None
    
    def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using local MMS TTS model"""
        try:
            if self.model is None or self.tokenizer is None:
                print("[TTS ERROR] Model not loaded properly")
                return None
                
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            print(f"[TTS] Processing text: {clean_text[:100]}...")
            
            # Tokenize input text
            inputs = self.tokenizer(clean_text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                # Generate audio
                outputs = self.model(**inputs)
                audio_array = outputs.waveform.squeeze().cpu().numpy()
            
            # Convert to bytes using soundfile
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, audio_array, samplerate=22050, format='WAV')
            audio_bytes = audio_buffer.getvalue()
            
            print(f"[TTS] Generated audio: {len(audio_bytes)} bytes")
            return audio_bytes
                
        except Exception as e:
            print(f"[TTS ERROR] Text-to-speech failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output with Vietnamese MMS model"""
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', ' ', text)
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Keep Vietnamese characters and basic punctuation
        text = re.sub(r'[^\w\s.,!?àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Limit length for MMS model (typically works better with shorter texts)
        if len(text) > 300:
            # Try to break at sentence boundaries
            sentences = re.split(r'[.!?]', text)
            text = ""
            for sentence in sentences:
                if len(text + sentence) > 300:
                    break
                text += sentence + ". "
            
            if not text:  # Fallback if no sentence breaks
                text = text[:300] + "..."
        
        # Ensure text ends with punctuation for better prosody
        text = text.strip()
        if text and text[-1] not in '.!?':
            text += "."
            
        return text
