import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_connectors import (
    EmbeddingAdapter, GoogleEmbeddingAdapter, HuggingFaceEmbeddingAdapter, 
    LocalEmbeddingAdapter, EmbeddingAdapterFactory,
    EmbeddingError, ModelLoadError, EmbeddingGenerationError, ConfigurationError
)


class TestEmbeddingAdapter(unittest.TestCase):
    """Test the abstract base class"""
    
    def test_abstract_methods(self):
        with self.assertRaises(TypeError):
            EmbeddingAdapter()


class TestGoogleEmbeddingAdapter(unittest.TestCase):
    
    def setUp(self):
        self.mock_embeddings = Mock()
        self.mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_init_success(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        
        self.assertEqual(adapter.model_name, "test-model")
        self.assertEqual(adapter.api_key, "test-api-key")
        mock_google_embeddings.assert_called_once_with(
            model="test-model",
            google_api_key="test-api-key"
        )

    def test_init_empty_model_name(self):
        with self.assertRaises(ValueError) as context:
            GoogleEmbeddingAdapter("", "test-api-key")
        
        self.assertIn("Model name cannot be empty", str(context.exception))

    def test_init_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError) as context:
                GoogleEmbeddingAdapter("test-model")
            
            self.assertIn("Google API key must be provided", str(context.exception))

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'env-key'})
    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_init_api_key_from_env(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model")
        
        self.assertEqual(adapter.api_key, "env-key")

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_init_model_load_error(self, mock_google_embeddings):
        mock_google_embeddings.side_effect = Exception("Model load failed")
        
        with self.assertRaises(ModelLoadError) as context:
            GoogleEmbeddingAdapter("test-model", "test-api-key")
        
        self.assertIn("Failed to initialize Google embeddings model", str(context.exception))

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_documents_success(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        result = adapter.embed_documents(["text1", "text2"])
        
        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        self.mock_embeddings.embed_documents.assert_called_once_with(["text1", "text2"])

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_documents_none_input(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        
        with self.assertRaises(ValueError) as context:
            adapter.embed_documents(None)
        
        self.assertIn("Texts list cannot be None", str(context.exception))

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_documents_empty_list(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        result = adapter.embed_documents([])
        
        self.assertEqual(result, [])

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_documents_generation_error(self, mock_google_embeddings):
        self.mock_embeddings.embed_documents.side_effect = Exception("Generation failed")
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        
        with self.assertRaises(EmbeddingGenerationError) as context:
            adapter.embed_documents(["text1"])
        
        self.assertIn("Failed to generate embeddings for documents", str(context.exception))

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_query_success(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        result = adapter.embed_query("test query")
        
        self.assertEqual(result, [0.1, 0.2, 0.3])
        self.mock_embeddings.embed_query.assert_called_once_with("test query")

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_query_none_input(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        
        with self.assertRaises(ValueError) as context:
            adapter.embed_query(None)
        
        self.assertIn("Text cannot be None", str(context.exception))

    @patch('model_connectors.GoogleGenerativeAIEmbeddings')
    def test_embed_query_empty_text(self, mock_google_embeddings):
        mock_google_embeddings.return_value = self.mock_embeddings
        
        adapter = GoogleEmbeddingAdapter("test-model", "test-api-key")
        
        with self.assertRaises(ValueError) as context:
            adapter.embed_query("   ")
        
        self.assertIn("Text cannot be empty", str(context.exception))


class TestHuggingFaceEmbeddingAdapter(unittest.TestCase):
    
    def setUp(self):
        self.mock_embeddings = Mock()
        self.mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]

    @patch('model_connectors.HuggingFaceEndpointEmbeddings')
    def test_init_success(self, mock_hf_embeddings):
        mock_hf_embeddings.return_value = self.mock_embeddings
        
        adapter = HuggingFaceEmbeddingAdapter("test-model", "test-api-key")
        
        self.assertEqual(adapter.model_name, "test-model")
        self.assertEqual(adapter.api_key, "test-api-key")
        mock_hf_embeddings.assert_called_once_with(
            model="test-model",
            huggingfacehub_api_token="test-api-key"
        )

    def test_init_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError) as context:
                HuggingFaceEmbeddingAdapter("test-model")
            
            self.assertIn("HuggingFace API key must be provided", str(context.exception))

    @patch.dict(os.environ, {'HF_API_KEY': 'env-key'})
    @patch('model_connectors.HuggingFaceEndpointEmbeddings')
    def test_init_api_key_from_env(self, mock_hf_embeddings):
        mock_hf_embeddings.return_value = self.mock_embeddings
        
        adapter = HuggingFaceEmbeddingAdapter("test-model")
        
        self.assertEqual(adapter.api_key, "env-key")

    @patch('model_connectors.HuggingFaceEndpointEmbeddings')
    def test_embed_documents_success(self, mock_hf_embeddings):
        mock_hf_embeddings.return_value = self.mock_embeddings
        
        adapter = HuggingFaceEmbeddingAdapter("test-model", "test-api-key")
        result = adapter.embed_documents(["text1", "text2"])
        
        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])


class TestLocalEmbeddingAdapter(unittest.TestCase):
    
    def setUp(self):
        self.mock_model = Mock()
        
        # Mock numpy array with tolist method
        mock_embeddings_array = Mock()
        mock_embeddings_array.tolist.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        mock_single_embedding_array = Mock()
        mock_single_embedding_array.tolist.return_value = [0.1, 0.2, 0.3]
        
        self.mock_model.encode.side_effect = [mock_embeddings_array, mock_single_embedding_array]

    @patch('model_connectors.SentenceTransformer')
    def test_init_success(self, mock_sentence_transformer):
        mock_sentence_transformer.return_value = self.mock_model
        
        adapter = LocalEmbeddingAdapter("test-model")
        
        self.assertEqual(adapter.model_name, "test-model")
        mock_sentence_transformer.assert_called_once_with("test-model")

    @patch('model_connectors.SentenceTransformer')
    def test_init_default_model(self, mock_sentence_transformer):
        mock_sentence_transformer.return_value = self.mock_model
        
        adapter = LocalEmbeddingAdapter()
        
        self.assertEqual(adapter.model_name, "paraphrase-multilingual-MiniLM-L12-v2")

    def test_init_empty_model_name(self):
        with self.assertRaises(ValueError) as context:
            LocalEmbeddingAdapter("")
        
        self.assertIn("Model name cannot be empty", str(context.exception))

    @patch('model_connectors.SentenceTransformer')
    def test_init_model_load_error(self, mock_sentence_transformer):
        mock_sentence_transformer.side_effect = Exception("Model load failed")
        
        with self.assertRaises(ModelLoadError) as context:
            LocalEmbeddingAdapter("test-model")
        
        self.assertIn("Failed to load local embeddings model", str(context.exception))

    @patch('model_connectors.SentenceTransformer')
    def test_embed_documents_success(self, mock_sentence_transformer):
        mock_sentence_transformer.return_value = self.mock_model
        
        adapter = LocalEmbeddingAdapter("test-model")
        result = adapter.embed_documents(["text1", "text2"])
        
        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        self.mock_model.encode.assert_called_with(
            ["text1", "text2"], 
            convert_to_tensor=False, 
            normalize_embeddings=True
        )

    @patch('model_connectors.SentenceTransformer')
    def test_embed_documents_empty_list(self, mock_sentence_transformer):
        mock_sentence_transformer.return_value = self.mock_model
        
        adapter = LocalEmbeddingAdapter("test-model")
        result = adapter.embed_documents([])
        
        self.assertEqual(result, [])

    @patch('model_connectors.SentenceTransformer')
    def test_embed_query_success(self, mock_sentence_transformer):
        # Setup separate mock for single embedding
        mock_single_array = Mock()
        mock_single_array.tolist.return_value = [0.1, 0.2, 0.3]
        self.mock_model.encode.return_value = [mock_single_array]
        
        mock_sentence_transformer.return_value = self.mock_model
        
        adapter = LocalEmbeddingAdapter("test-model")
        result = adapter.embed_query("test query")
        
        self.assertEqual(result, [0.1, 0.2, 0.3])
        self.mock_model.encode.assert_called_with(
            ["test query"], 
            convert_to_tensor=False, 
            normalize_embeddings=True
        )


class TestEmbeddingAdapterFactory(unittest.TestCase):
    
    @patch('model_connectors.GoogleEmbeddingAdapter')
    def test_create_adapter_google(self, mock_google_adapter):
        mock_adapter_instance = Mock()
        mock_google_adapter.return_value = mock_adapter_instance
        
        result = EmbeddingAdapterFactory.create_adapter("test-model", "google", "api-key")
        
        self.assertEqual(result, mock_adapter_instance)
        mock_google_adapter.assert_called_once_with("test-model", "api-key")

    @patch('model_connectors.HuggingFaceEmbeddingAdapter')
    def test_create_adapter_huggingface(self, mock_hf_adapter):
        mock_adapter_instance = Mock()
        mock_hf_adapter.return_value = mock_adapter_instance
        
        result = EmbeddingAdapterFactory.create_adapter("test-model", "huggingface", "api-key")
        
        self.assertEqual(result, mock_adapter_instance)
        mock_hf_adapter.assert_called_once_with("test-model", "api-key")

    @patch('model_connectors.LocalEmbeddingAdapter')
    def test_create_adapter_local(self, mock_local_adapter):
        mock_adapter_instance = Mock()
        mock_local_adapter.return_value = mock_adapter_instance
        
        result = EmbeddingAdapterFactory.create_adapter("test-model", "local")
        
        self.assertEqual(result, mock_adapter_instance)
        mock_local_adapter.assert_called_once_with("test-model")

    def test_create_adapter_unknown_provider(self):
        with self.assertRaises(ValueError) as context:
            EmbeddingAdapterFactory.create_adapter("test-model", "unknown")
        
        self.assertIn("Unknown provider: unknown", str(context.exception))

    def test_create_adapter_empty_model_name(self):
        with self.assertRaises(ValueError) as context:
            EmbeddingAdapterFactory.create_adapter("", "google")
        
        self.assertIn("Model name cannot be empty", str(context.exception))

    def test_create_adapter_empty_provider(self):
        with self.assertRaises(ValueError) as context:
            EmbeddingAdapterFactory.create_adapter("test-model", "")
        
        self.assertIn("Provider cannot be empty", str(context.exception))

    def test_create_adapter_case_insensitive_provider(self):
        with patch('model_connectors.GoogleEmbeddingAdapter') as mock_google_adapter:
            mock_adapter_instance = Mock()
            mock_google_adapter.return_value = mock_adapter_instance
            
            result = EmbeddingAdapterFactory.create_adapter("test-model", "GOOGLE", "api-key")
            
            self.assertEqual(result, mock_adapter_instance)

    @patch('model_connectors.GoogleEmbeddingAdapter')
    def test_create_from_config_success(self, mock_google_adapter):
        mock_adapter_instance = Mock()
        mock_google_adapter.return_value = mock_adapter_instance
        
        config = {
            'model_name': 'test-model',
            'provider': 'google',
            'api_key': 'api-key'
        }
        
        result = EmbeddingAdapterFactory.create_from_config(config)
        
        self.assertEqual(result, mock_adapter_instance)

    def test_create_from_config_none_config(self):
        with self.assertRaises(ValueError) as context:
            EmbeddingAdapterFactory.create_from_config(None)
        
        self.assertIn("Config cannot be None", str(context.exception))

    def test_create_from_config_non_dict(self):
        with self.assertRaises(ValueError) as context:
            EmbeddingAdapterFactory.create_from_config("not a dict")
        
        self.assertIn("Config must be a dictionary", str(context.exception))

    def test_create_from_config_missing_provider(self):
        config = {'model_name': 'test-model'}
        
        with self.assertRaises(ConfigurationError) as context:
            EmbeddingAdapterFactory.create_from_config(config)
        
        self.assertIn("Provider must be specified in config", str(context.exception))

    def test_create_from_config_missing_model_name(self):
        config = {'provider': 'google'}
        
        with self.assertRaises(ConfigurationError) as context:
            EmbeddingAdapterFactory.create_from_config(config)
        
        self.assertIn("Model name must be specified in config", str(context.exception))

    @patch('model_connectors.LocalEmbeddingAdapter')
    def test_create_from_config_local_no_api_key(self, mock_local_adapter):
        mock_adapter_instance = Mock()
        mock_local_adapter.return_value = mock_adapter_instance
        
        config = {
            'model_name': 'test-model',
            'provider': 'local'
        }
        
        result = EmbeddingAdapterFactory.create_from_config(config)
        
        self.assertEqual(result, mock_adapter_instance)
        mock_local_adapter.assert_called_once_with("test-model")


if __name__ == '__main__':
    unittest.main()