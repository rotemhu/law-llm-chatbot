import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storers import (
    PineconeStorer, PostgreSqlStorer, Storer,
    StorerError, DatabaseConnectionError, StorageError, ConfigurationError
)
from model_connectors import EmbeddingAdapter


class MockEmbeddingAdapter(EmbeddingAdapter):
    """Mock embedding adapter for testing"""
    
    def embed_documents(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]
    
    def embed_query(self, text):
        return [0.1, 0.2, 0.3]


class TestStorer(unittest.TestCase):
    
    def test_store_not_implemented(self):
        storer = Storer()
        with self.assertRaises(NotImplementedError):
            storer.store("test")


class TestPineconeStorer(unittest.TestCase):
    
    def setUp(self):
        self.mock_embedding_adapter = MockEmbeddingAdapter()
        self.sample_chunks = [
            {
                'text': 'חוק הבטיחות - סעיף ראשון',
                'law_name': 'חוק הבטיחות',
                'section': '1'
            },
            {
                'text': 'חוק הבטיחות - סעיף שני',
                'law_name': 'חוק הבטיחות', 
                'section': '2'
            }
        ]

    def test_init_with_embedding_adapter(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            self.assertEqual(storer.api_key, "test_key")
            self.assertEqual(storer.embedding_adapter, self.mock_embedding_adapter)

    def test_init_with_embedding_config(self):
        with patch('storers.Pinecone') as mock_pinecone, \
             patch('storers.EmbeddingAdapterFactory') as mock_factory:
            
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            mock_factory.create_from_config.return_value = self.mock_embedding_adapter
            
            config = {'provider': 'local', 'model_name': 'test-model'}
            storer = PineconeStorer(
                api_key="test_key",
                embedding_config=config
            )
            
            mock_factory.create_from_config.assert_called_once_with(config)

    def test_init_default_embedding_adapter(self):
        with patch('storers.Pinecone') as mock_pinecone, \
             patch('storers.EmbeddingAdapterFactory') as mock_factory:
            
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            mock_factory.create_from_config.return_value = self.mock_embedding_adapter
            
            storer = PineconeStorer(api_key="test_key")
            
            expected_config = {'provider': 'local', 'model_name': 'paraphrase-multilingual-MiniLM-L12-v2'}
            mock_factory.create_from_config.assert_called_once_with(expected_config)

    def test_init_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError) as context:
                PineconeStorer()
            
            self.assertIn("Pinecone API key must be provided", str(context.exception))

    def test_init_api_key_from_env(self):
        with patch.dict(os.environ, {'PINECONE_API_KEY': 'env_key'}), \
             patch('storers.Pinecone') as mock_pinecone, \
             patch('storers.EmbeddingAdapterFactory') as mock_factory:
            
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            mock_factory.create_from_config.return_value = self.mock_embedding_adapter
            
            storer = PineconeStorer()
            
            self.assertEqual(storer.api_key, 'env_key')

    def test_init_invalid_embedding_adapter(self):
        with self.assertRaises(ValueError) as context:
            PineconeStorer(
                api_key="test_key",
                embedding_adapter="not_an_adapter"
            )
        
        self.assertIn("embedding_adapter must be an instance of EmbeddingAdapter", str(context.exception))

    def test_init_invalid_embedding_config(self):
        with self.assertRaises(ValueError) as context:
            PineconeStorer(
                api_key="test_key",
                embedding_config="not_a_dict"
            )
        
        self.assertIn("embedding_config must be a dictionary", str(context.exception))

    def test_init_empty_index_name(self):
        with self.assertRaises(ValueError) as context:
            PineconeStorer(
                api_key="test_key",
                index_name="",
                embedding_adapter=self.mock_embedding_adapter
            )
        
        self.assertIn("Index name cannot be empty", str(context.exception))

    def test_init_invalid_dimension(self):
        with self.assertRaises(ValueError) as context:
            PineconeStorer(
                api_key="test_key",
                dimension=0,
                embedding_adapter=self.mock_embedding_adapter
            )
        
        self.assertIn("Dimension must be positive", str(context.exception))

    def test_init_pinecone_connection_error(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pinecone.side_effect = Exception("Connection failed")
            
            with self.assertRaises(DatabaseConnectionError) as context:
                PineconeStorer(
                    api_key="test_key",
                    embedding_adapter=self.mock_embedding_adapter
                )
            
            self.assertIn("Failed to connect to Pinecone", str(context.exception))

    def test_ensure_index_exists_creates_new_index(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = []
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                index_name="new-index",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            mock_pc.create_index.assert_called_once()

    def test_ensure_index_exists_index_already_exists(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['law-agent']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            mock_pc.create_index.assert_not_called()

    def test_generate_embeddings_success(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            texts = ["text1", "text2"]
            result = storer._generate_embeddings(texts)
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], [0.1, 0.2, 0.3])

    def test_generate_embeddings_none_input(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            with self.assertRaises(ValueError) as context:
                storer._generate_embeddings(None)
            
            self.assertIn("Texts list cannot be None", str(context.exception))

    def test_generate_embeddings_empty_list(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            result = storer._generate_embeddings([])
            self.assertEqual(result, [])

    def test_store_success(self):
        with patch('storers.Pinecone') as mock_pinecone, \
             patch('storers.uuid.uuid4') as mock_uuid:
            
            mock_pc = Mock()
            mock_index = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = mock_index
            mock_pinecone.return_value = mock_pc
            
            mock_uuid.return_value.hex = "test-uuid-123"
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            result = storer.store(self.sample_chunks)
            
            self.assertEqual(len(result), 2)
            self.assertIn('id', result[0])
            self.assertIn('values', result[0])
            self.assertIn('metadata', result[0])
            
            mock_index.upsert.assert_called_once()

    def test_store_with_provided_embeddings(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_index = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = mock_index
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            embeddings = [[0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
            result = storer.store(self.sample_chunks, embeddings)
            
            self.assertEqual(result[0]['values'], [0.4, 0.5, 0.6])
            self.assertEqual(result[1]['values'], [0.7, 0.8, 0.9])

    def test_store_none_chunks(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            with self.assertRaises(ValueError) as context:
                storer.store(None)
            
            self.assertIn("chunks_to_store cannot be None", str(context.exception))

    def test_store_empty_chunks(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            result = storer.store([])
            self.assertEqual(result, [])

    def test_store_invalid_chunk_structure(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            invalid_chunks = [{'no_text_field': 'value'}]
            
            with self.assertRaises(ValueError) as context:
                storer.store(invalid_chunks)
            
            self.assertIn("must contain 'text' field", str(context.exception))

    def test_store_mismatched_embeddings_count(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = Mock()
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            embeddings = [[0.1, 0.2, 0.3]]  # Only one embedding for two chunks
            
            with self.assertRaises(ValueError) as context:
                storer.store(self.sample_chunks, embeddings)
            
            self.assertIn("Number of embeddings must match", str(context.exception))

    def test_store_batch_processing(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_index = Mock()
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = mock_index
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            # Create 150 chunks to test batching (batch size is 100)
            large_chunks = []
            for i in range(150):
                large_chunks.append({
                    'text': f'Text {i}',
                    'law_name': 'Test Law',
                    'section': str(i)
                })
            
            storer.store(large_chunks)
            
            # Should call upsert twice (100 + 50)
            self.assertEqual(mock_index.upsert.call_count, 2)

    def test_store_upsert_error(self):
        with patch('storers.Pinecone') as mock_pinecone:
            mock_pc = Mock()
            mock_index = Mock()
            mock_index.upsert.side_effect = Exception("Upsert failed")
            mock_pc.list_indexes.return_value.names.return_value = ['existing-index']
            mock_pc.Index.return_value = mock_index
            mock_pinecone.return_value = mock_pc
            
            storer = PineconeStorer(
                api_key="test_key",
                embedding_adapter=self.mock_embedding_adapter
            )
            
            with self.assertRaises(StorageError) as context:
                storer.store(self.sample_chunks)
            
            self.assertIn("Failed to upsert vectors to Pinecone", str(context.exception))


class TestPostgreSqlStorer(unittest.TestCase):
    
    def test_init_success(self):
        storer = PostgreSqlStorer("postgresql://user:pass@host/db", "test_table")
        
        self.assertEqual(storer._connection_string, "postgresql://user:pass@host/db")
        self.assertEqual(storer._table_name, "test_table")
        self.assertIsNone(storer._schema)

    def test_init_with_schema(self):
        storer = PostgreSqlStorer("postgresql://user:pass@host/db", "test_table", "public")
        
        self.assertEqual(storer._schema, "public")

    def test_init_empty_connection_string(self):
        with self.assertRaises(ValueError) as context:
            PostgreSqlStorer("", "test_table")
        
        self.assertIn("Connection string cannot be empty", str(context.exception))

    def test_init_empty_table_name(self):
        with self.assertRaises(ValueError) as context:
            PostgreSqlStorer("postgresql://user:pass@host/db", "")
        
        self.assertIn("Table name cannot be empty", str(context.exception))

    def test_init_empty_schema(self):
        with self.assertRaises(ValueError) as context:
            PostgreSqlStorer("postgresql://user:pass@host/db", "test_table", "")
        
        self.assertIn("Schema cannot be empty if provided", str(context.exception))

    def test_store_not_implemented(self):
        storer = PostgreSqlStorer("postgresql://user:pass@host/db", "test_table")
        
        with self.assertRaises(NotImplementedError) as context:
            storer.store("test_resource")
        
        self.assertIn("PostgreSQL storage is not yet implemented", str(context.exception))


if __name__ == '__main__':
    unittest.main()