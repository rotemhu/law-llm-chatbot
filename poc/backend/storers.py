
from pinecone import Pinecone, ServerlessSpec
import os
from typing import List, Dict, Any, Optional
import uuid
from model_connectors import EmbeddingAdapter, EmbeddingAdapterFactory

class StorerError(Exception):
    """Base exception for storer operations"""
    pass

class DatabaseConnectionError(StorerError):
    """Exception for database connection errors"""
    pass

class StorageError(StorerError):
    """Exception for storage operation errors"""
    pass

class ConfigurationError(StorerError):
    """Exception for configuration errors"""
    pass

class Storer:
    def __init__(self):
        pass

    def store(self, resource):
        """
        Store a resource.
        
        Args:
            resource: The resource to store
            
        Raises:
            NotImplementedError: This is an abstract method
        """
        raise NotImplementedError("Subclasses must implement store method")

class VectorDbStorer(Storer):
    pass

class PineconeStorer(VectorDbStorer):
    def __init__(self, 
                 api_key: str = None, 
                 index_name: str = "law-agent", 
                 dimension: int = 1024,
                 embedding_adapter: EmbeddingAdapter = None,
                 embedding_config: Dict[str, Any] = None):
        """
        Initialize PineconeStorer with embedding adapter
        
        Args:
            api_key: Pinecone API key
            index_name: Pinecone index name
            dimension: Pinecone index dimension(should be same as embedding model dimension)
            embedding_adapter: Pre-configured embedding adapter
            embedding_config: Configuration for creating embedding adapter
            
        Raises:
            ValueError: If parameters are invalid
            ConfigurationError: If configuration is invalid
            DatabaseConnectionError: If connection fails
        """
        super().__init__()
        
        # Validate inputs
        if index_name and not index_name.strip():
            raise ValueError("Index name cannot be empty")
        
        if dimension and dimension <= 0:
            raise ValueError("Dimension must be positive")
        
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.index_name = index_name or "law-agent"
        
        if not self.api_key:
            raise ConfigurationError("Pinecone API key must be provided either as parameter or PINECONE_API_KEY environment variable")
        
        # Set up embedding adapter
        try:
            if embedding_adapter:
                if not isinstance(embedding_adapter, EmbeddingAdapter):
                    raise ValueError("embedding_adapter must be an instance of EmbeddingAdapter")
                self.embedding_adapter = embedding_adapter
            elif embedding_config:
                if not isinstance(embedding_config, dict):
                    raise ValueError("embedding_config must be a dictionary")
                self.embedding_adapter = EmbeddingAdapterFactory.create_from_config(embedding_config)
            else:
                # Create default local embedding adapter
                default_config = {'provider': 'local', 'model_name': 'paraphrase-multilingual-MiniLM-L12-v2'}
                self.embedding_adapter = EmbeddingAdapterFactory.create_from_config(default_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to set up embedding adapter: {e}")
        
        self.dimension = dimension
        
        # Initialize Pinecone connection
        try:
            self.pc = Pinecone(api_key=self.api_key)
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to Pinecone: {e}")
        
        try:
            self._ensure_index_exists()
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to access Pinecone index '{self.index_name}': {e}")
    
    def _ensure_index_exists(self):
        """
        Create index if it doesn't exist
        
        Raises:
            DatabaseConnectionError: If index creation fails
        """
        try:
            existing_indexes = self.pc.list_indexes()
            
            if self.index_name not in existing_indexes.names():
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to ensure index exists: {e}")
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using the configured adapter
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If texts is invalid
            StorageError: If embedding generation fails
        """
        if texts is None:
            raise ValueError("Texts list cannot be None")
        
        if not isinstance(texts, list):
            raise ValueError("Texts must be a list")
        
        if not texts:
            return []
        
        try:
            return self.embedding_adapter.embed_documents(texts)
        except Exception as e:
            raise StorageError(f"Failed to generate embeddings: {e}")
    
    def store(self, chunks_to_store: List[Dict[str, Any]], embeddings: List[List[float]] = None) -> List[Dict[str, Any]]:
        """
        Store data into Pinecone DB.
        
        Args:
            chunks_to_store: List of dictionaries which represents the data 
                        should be stored divided to chunks(with metadata).
                        Each chunk should have 'text' field and optional metadata fields:
                        'law_name', 'part', 'chapter', 'sign', 'section'
            embeddings: Optional list of embedding vectors. If not provided, 
                       will generate them using the configured embedding model.
        Returns:
            list of chunks, with metadata and id in Pinecone DB for
              each chunk.
        Raises:
            ValueError: If inputs are invalid
            StorageError: If storage operation fails
        """
        if chunks_to_store is None:
            raise ValueError("chunks_to_store cannot be None")
        
        if not isinstance(chunks_to_store, list):
            raise ValueError("chunks_to_store must be a list")
        
        if not chunks_to_store:
            return []
        
        # Validate chunks structure
        for i, chunk in enumerate(chunks_to_store):
            if not isinstance(chunk, dict):
                raise ValueError(f"Chunk at index {i} must be a dictionary")
            if 'text' not in chunk:
                raise ValueError(f"Chunk at index {i} must contain 'text' field")
        
        if embeddings is not None:
            if not isinstance(embeddings, list):
                raise ValueError("embeddings must be a list")
            if len(embeddings) != len(chunks_to_store):
                raise ValueError("Number of embeddings must match number of parsed data items")
            
            # Validate embedding structure
            for i, embedding in enumerate(embeddings):
                if not embedding:
                    raise ValueError(f"Embedding at index {i} cannot be empty")
                if not isinstance(embedding, list):
                    raise ValueError(f"Embedding at index {i} must be a list")
        
        try:
            # Generate embeddings if not provided
            if embeddings is None:
                texts = [item.get('text', '') for item in chunks_to_store]
                embeddings = self._generate_embeddings(texts)
            
            vectors = []
            
            for i, item in enumerate(chunks_to_store):
                try:
                    # Create metadata from all attributes except 'text'
                    metadata = {
                        'law_name': item.get('law_name'),
                        'part': item.get('part'),
                        'chapter': item.get('chapter'), 
                        'sign': item.get('sign'),
                        'section': item.get('section')
                    }
                    
                    # Remove None values from metadata
                    metadata = {k: v for k, v in metadata.items() if v is not None}
                    
                    # Create unique ID for the vector
                    vector_id = str(uuid.uuid4())
                    
                    vector_data = {
                        'id': vector_id,
                        'values': embeddings[i],
                        'metadata': {
                            **metadata,
                            'text': item.get('text', '')
                        }
                    }
                    
                    vectors.append(vector_data)
                except Exception as e:
                    raise StorageError(f"Failed to process chunk at index {i}: {e}")
            
            # Batch upsert to Pinecone (max 100 vectors per batch)
            batch_size = 100
            try:
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch)
            except Exception as e:
                raise StorageError(f"Failed to upsert vectors to Pinecone: {e}")
            
            return vectors
            
        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            raise StorageError(f"Unexpected error during storage operation: {e}")

class RelationalDbStorer(Storer):
    pass

class PostgreSqlStorer(RelationalDbStorer):
    def __init__(self, con_str: str, table_name: str, schema = None):
        """
        Initialize PostgreSQL storer.
        
        Args:
            con_str: Database connection string
            table_name: Name of the table to store data
            schema: Optional schema name
            
        Raises:
            ValueError: If parameters are invalid
            ConfigurationError: If configuration is invalid
        """
        if not con_str or not con_str.strip():
            raise ValueError("Connection string cannot be empty")
        
        if not table_name or not table_name.strip():
            raise ValueError("Table name cannot be empty")
        
        if schema is not None and not schema.strip():
            raise ValueError("Schema cannot be empty if provided")
        
        self._connection_string = con_str
        self._table_name = table_name
        self._schema = schema
    
    def store(self, resource):
        """
        Store resource in PostgreSQL database.
        
        Args:
            resource: The resource to store
            
        Raises:
            NotImplementedError: This method is not yet implemented
        """
        raise NotImplementedError("PostgreSQL storage is not yet implemented")
