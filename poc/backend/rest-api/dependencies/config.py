import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    app_name: str = "Israeli Law Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Google Gemini Configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = "gemini-1.5-flash"
    
    # Pinecone Configuration
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = "law-agent"
    pinecone_dimension: int = 768
    
    # Embedding Configuration
    embedding_provider: str = "google"
    embedding_model: str = "models/embedding-001"
    
    # RAG Configuration
    max_relevant_documents: int = 5
    similarity_threshold: float = 0.7
    
    # Response Configuration
    default_max_tokens: int = 1000
    default_temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()