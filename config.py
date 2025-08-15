import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION')
    
    # Azure OpenAI Embedding Service
    AZURE_OPENAI_EMBEDDING_API_KEY = os.environ.get('AZURE_OPENAI_EMBEDDING_API_KEY')
    AZURE_OPENAI_EMBEDDING_ENDPOINT = os.environ.get('AZURE_OPENAI_EMBEDDING_ENDPOINT')
    AZURE_OPENAI_EMBEDDING_API_VERSION = os.environ.get('AZURE_OPENAI_EMBEDDING_API_VERSION')
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-small')
    
    # Model parameters
    AZURE_OPENAI_TEMPERATURE = float(os.environ.get('AZURE_OPENAI_TEMPERATURE', '1.0'))  # Default to 1.0 for GPT-5
    
    # Hugging Face
    HUGGINGFACE_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN')
    
    # Admin
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    
    # ChromaDB
    CHROMADB_PATH = os.environ.get('CHROMADB_PATH') or './data/chroma_db'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
