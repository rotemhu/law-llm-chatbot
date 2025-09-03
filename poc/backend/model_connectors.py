from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from sentence_transformers import SentenceTransformer

class EmbeddingError(Exception):
    """Base exception for embedding operations"""
    pass

class ModelLoadError(EmbeddingError):
    """Exception for model loading errors"""
    pass

class EmbeddingGenerationError(EmbeddingError):
    """Exception for embedding generation errors"""
    pass

class ConfigurationError(EmbeddingError):
    """Exception for configuration errors"""
    pass

class EmbeddingAdapter(ABC):
    """Abstract base class for embedding model adapters"""
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents
        
        Args:
            texts: List of document texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If texts is None or contains invalid items
            EmbeddingGenerationError: If embedding generation fails
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            ValueError: If text is None or empty
            EmbeddingGenerationError: If embedding generation fails
        """
        pass
    


class GoogleEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for Google embeddings"""
    
    def __init__(self, model_name: str = "models/embedding-001", api_key: Optional[str] = None):
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty")
        
        self.model_name = model_name
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ConfigurationError("Google API key must be provided via parameter or GOOGLE_API_KEY environment variable")
        
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key=self.api_key
            )
        except Exception as e:
            raise ModelLoadError(f"Failed to initialize Google embeddings model '{model_name}': {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        if texts is None:
            raise ValueError("Texts list cannot be None")
        
        if not isinstance(texts, list):
            raise ValueError("Texts must be a list")
        
        if not texts:
            return []
        
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embeddings for documents: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        if text is None:
            raise ValueError("Text cannot be None")
        
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embedding for query: {e}")



class HuggingFaceEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for HuggingFace Inference embeddings"""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty")
        
        self.model_name = model_name
        self.api_key = api_key or os.getenv('HF_API_KEY')
        
        if not self.api_key:
            raise ConfigurationError("HuggingFace API key must be provided via parameter or HF_API_KEY environment variable")
        
        try:
            self.embeddings = HuggingFaceEndpointEmbeddings(
                model=model_name,
                huggingfacehub_api_token=self.api_key
            )
        except Exception as e:
            raise ModelLoadError(f"Failed to initialize HuggingFace embeddings model '{model_name}': {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        if texts is None:
            raise ValueError("Texts list cannot be None")
        
        if not isinstance(texts, list):
            raise ValueError("Texts must be a list")
        
        if not texts:
            return []
        
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embeddings for documents: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        if text is None:
            raise ValueError("Text cannot be None")
        
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embedding for query: {e}")


class LocalEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for HuggingFace embeddings(Local instance)"""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty")
        
        self.model_name = model_name
        
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise ModelLoadError(f"Failed to load local embeddings model '{model_name}': {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        if texts is None:
            raise ValueError("Texts list cannot be None")
        
        if not isinstance(texts, list):
            raise ValueError("Texts must be a list")
        
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embeddings for documents: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        if text is None:
            raise ValueError("Text cannot be None")
        
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            embedding = self.model.encode([text], convert_to_tensor=False, normalize_embeddings=True)
            return embedding[0].tolist()
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embedding for query: {e}")
    
    # @property
    # def dimension(self) -> int:
    #     """Return embedding dimension from model"""
    #     return self.model.get_sentence_embedding_dimension()


class EmbeddingAdapterFactory:
    """Factory class for creating embedding adapters"""
    
    @staticmethod
    def create_adapter(
        model_name: str,
        provider: str,
        api_key: Optional[str] = None,
    ) -> EmbeddingAdapter:
        """
        Create an embedding adapter based on model name and provider
        
        Args:
            model_name: Name of the embedding model
            provider: provider hint ("google", "huggingface", "local")
            api_key: Optional API key for cloud providers

        Returns:
            EmbeddingAdapter instance
            
        Raises:
            ValueError: If parameters are invalid
            ConfigurationError: If configuration is invalid
            ModelLoadError: If model loading fails
        """
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty")
        
        if not provider or not provider.strip():
            raise ValueError("Provider cannot be empty")
        
        provider = provider.lower().strip()
        
        # Create adapter based on provider
        try:
            if provider == "google":
                return GoogleEmbeddingAdapter(model_name, api_key)
            elif provider == "huggingface":
                return HuggingFaceEmbeddingAdapter(model_name, api_key)
            elif provider == "local":
                return LocalEmbeddingAdapter(model_name)
            else:
                raise ValueError(f"Unknown provider: {provider}. Supported providers: google, huggingface, local")
        except Exception as e:
            if isinstance(e, (ValueError, ConfigurationError, ModelLoadError)):
                raise
            raise EmbeddingError(f"Failed to create embedding adapter: {e}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> EmbeddingAdapter:
        """
        Create adapter from configuration dictionary
        
        Args:
            config: Configuration dictionary with model_name, provider, api_key
            
        Returns:
            EmbeddingAdapter instance
            
        Raises:
            ValueError: If config is invalid
            ConfigurationError: If required configuration is missing
        """
        if config is None:
            raise ValueError("Config cannot be None")
        
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        
        provider = config.get('provider')
        if not provider:
            raise ConfigurationError("Provider must be specified in config")
        
        model_name = config.get('model_name')
        if not model_name:
            raise ConfigurationError("Model name must be specified in config for this provider")
        
        return EmbeddingAdapterFactory.create_adapter(
            model_name=model_name,
            provider=provider,
            api_key=config.get('api_key'),
        )
    
    # @staticmethod
    # def create_from_env() -> EmbeddingAdapter:
    #     """Create adapter from environment variables"""
    #     config = {
    #         'model_name': os.getenv('EMBEDDING_MODEL', 'models/embedding-001'),
    #         'provider': os.getenv('EMBEDDING_PROVIDER'),
    #         'api_key': os.getenv('GOOGLE_API_KEY'),
    #     }
    #     return EmbeddingAdapterFactory.create_from_config(config)