import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import AzureOpenAI
import os
from config import Config

class ChromaDBManager:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
        self.collection_name = "travel_knowledge"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embeddings client
        self.embedding_client = AzureOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_EMBEDDING_ENDPOINT,
            api_key=Config.AZURE_OPENAI_EMBEDDING_API_KEY,
            api_version=Config.AZURE_OPENAI_EMBEDDING_API_VERSION
        )
        self.embedding_deployment = Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    
    def add_documents(self, texts, metadatas=None):
        """Add documents to the ChromaDB collection"""
        try:
            # Create embeddings using AzureOpenAI client
            embeddings = []
            for text in texts:
                response = self.embedding_client.embeddings.create(
                    input=text,
                    model=self.embedding_deployment
                )
                embeddings.append(response.data[0].embedding)
            
            # Generate unique IDs
            import uuid
            import time
            timestamp = int(time.time())
            ids = [f"doc_{timestamp}_{i}" for i in range(len(texts))]
            
            # Add to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas or [{"source": "uploaded"} for _ in texts],
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def query_documents(self, query_text, n_results=5):
        """Query documents from ChromaDB"""
        try:
            # Create query embedding using AzureOpenAI client
            response = self.embedding_client.embeddings.create(
                input=query_text,
                model=self.embedding_deployment
            )
            query_embedding = response.data[0].embedding
            
            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results
        except Exception as e:
            print(f"Error querying documents: {e}")
            return None

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_text_file(self, file_path):
        """Process text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        chunks = self.text_splitter.split_text(content)
        return chunks
    
    def process_pdf_file(self, file_path):
        """Process PDF file"""
        try:
            import PyPDF2
            chunks = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                chunks = self.text_splitter.split_text(text)
            
            return chunks
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return []
    
    def process_docx_file(self, file_path):
        """Process DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            chunks = self.text_splitter.split_text(text)
            return chunks
        except Exception as e:
            print(f"Error processing DOCX: {e}")
            return []
