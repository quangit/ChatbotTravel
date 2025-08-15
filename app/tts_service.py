import requests
import io
from config import Config

class TTSService:
    def __init__(self):
        self.api_token = Config.HUGGINGFACE_API_TOKEN
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
    
    def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using Hugging Face API"""
        try:
            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            payload = {
                "inputs": clean_text
            }
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"TTS API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"TTS Service Error: {e}")
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        import re
        
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', ' ', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s.,!?àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', '', text)
        
        # Limit length (TTS models often have input limits)
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text.strip()
