"""
Unit tests for embedding service.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from app.services.embedding_service import EmbeddingService, get_embedding_service


@pytest.fixture(autouse=True)
def reset_embedding_service():
    """Reset the singleton instance before each test."""
    # Reset the singleton instance
    EmbeddingService._instance = None
    EmbeddingService._model = None
    
    # Reset the global instance
    import app.services.embedding_service as embedding_module
    embedding_module._embedding_service = None
    
    yield
    
    # Cleanup after test
    EmbeddingService._instance = None
    EmbeddingService._model = None
    embedding_module._embedding_service = None


class TestEmbeddingServiceSingleton:
    """Test singleton pattern implementation."""
    
    def test_singleton_pattern(self):
        """Test that only one instance is created."""
        service1 = EmbeddingService()
        service2 = EmbeddingService()
        
        assert service1 is service2
        assert id(service1) == id(service2)
    
    def test_get_embedding_service_returns_singleton(self):
        """Test that get_embedding_service returns the same instance."""
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        
        assert service1 is service2


class TestEmbeddingServiceInitialization:
    """Test embedding service initialization."""
    
    def test_initialization(self):
        """Test that service initializes with correct settings."""
        service = EmbeddingService()
        
        assert service.model_name is not None
        assert service.device is not None
        assert service.batch_size is not None
        assert service._model is None  # Not loaded yet
        assert service._vector_size is None


class TestEmbeddingServiceModelLoading:
    """Test model loading functionality."""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_load_model_lazy_loading(self, mock_sentence_transformer):
        """Test that model is loaded lazily on first use."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        
        # Model should not be loaded yet
        assert service._model is None
        
        # Get model should trigger loading
        model = service.get_model()
        
        # Model should now be loaded
        assert service._model is not None
        assert model is mock_model
        mock_sentence_transformer.assert_called_once()
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_load_model_caches_instance(self, mock_sentence_transformer):
        """Test that model instance is cached."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_sentence_transformer.return_value = mock_model
        
        # Create fresh service instance
        service = EmbeddingService()
        service._model = None  # Ensure model is not loaded
        
        # Get model twice
        model1 = service.get_model()
        model2 = service.get_model()
        
        # Should return same instance
        assert model1 is model2
        # Should only create model once
        assert mock_sentence_transformer.call_count == 1
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_load_model_error_handling(self, mock_sentence_transformer):
        """Test error handling when model loading fails."""
        mock_sentence_transformer.side_effect = Exception("Model loading failed")
        
        service = EmbeddingService()
        service._model = None  # Ensure model is not loaded
        
        with pytest.raises(Exception, match="Model loading failed"):
            service.get_model()


class TestEmbeddingServiceEncode:
    """Test single text encoding."""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_single_text(self, mock_sentence_transformer):
        """Test encoding a single text."""
        # Setup mock model
        mock_model = Mock()
        mock_embedding = np.array([[0.1, 0.2, 0.3, 0.4]])  # 2D array
        mock_model.encode.return_value = mock_embedding
        mock_model.get_sentence_embedding_dimension.return_value = 4
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        result = service.encode("דירה יפה")
        
        # Should return 1D array
        assert result.ndim == 1
        assert result.shape == (4,)
        assert np.array_equal(result, mock_embedding[0])
        mock_model.encode.assert_called_once()
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_empty_text_raises_error(self, mock_sentence_transformer):
        """Test that encoding empty text raises ValueError."""
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.encode("")
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.encode("   ")
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_normalization(self, mock_sentence_transformer):
        """Test that normalization parameter is passed correctly."""
        mock_model = Mock()
        mock_embedding = np.array([[0.1, 0.2, 0.3]])
        mock_model.encode.return_value = mock_embedding
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        
        # Test with normalization=True (default)
        service.encode("test", normalize_embeddings=True)
        call_args = mock_model.encode.call_args
        assert call_args.kwargs["normalize_embeddings"] is True
        
        # Test with normalization=False
        service.encode("test2", normalize_embeddings=False)
        call_args = mock_model.encode.call_args
        assert call_args.kwargs["normalize_embeddings"] is False


class TestEmbeddingServiceEncodeBatch:
    """Test batch encoding."""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_batch(self, mock_sentence_transformer):
        """Test encoding a batch of texts."""
        # Setup mock model
        mock_model = Mock()
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ])
        mock_model.encode.return_value = mock_embeddings
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        texts = ["דירה יפה", "בית גדול", "דירה קטנה"]
        result = service.encode_batch(texts)
        
        # Should return 2D array
        assert result.ndim == 2
        assert result.shape == (3, 3)
        assert np.array_equal(result, mock_embeddings)
        mock_model.encode.assert_called_once()
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_batch_empty_list_raises_error(self, mock_sentence_transformer):
        """Test that encoding empty list raises ValueError."""
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            service.encode_batch([])
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_batch_uses_batch_size(self, mock_sentence_transformer):
        """Test that batch size from config is used."""
        mock_model = Mock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3]])
        mock_model.encode.return_value = mock_embeddings
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        texts = ["test"]
        service.encode_batch(texts)
        
        # Check that batch_size was passed
        call_args = mock_model.encode.call_args
        assert "batch_size" in call_args.kwargs
        assert call_args.kwargs["batch_size"] == service.batch_size


class TestEmbeddingServiceModelInfo:
    """Test model info methods."""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_get_model_info(self, mock_sentence_transformer):
        """Test getting model information."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        info = service.get_model_info()
        
        assert "model_name" in info
        assert "device" in info
        assert "vector_size" in info
        assert "batch_size" in info
        assert "is_loaded" in info
        assert info["vector_size"] == 768
        assert info["is_loaded"] is True
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_get_vector_size(self, mock_sentence_transformer):
        """Test getting vector size."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        vector_size = service.get_vector_size()
        
        assert vector_size == 768
        # Should be cached
        assert service._vector_size == 768
        vector_size2 = service.get_vector_size()
        assert vector_size2 == 768


class TestEmbeddingServiceHebrewText:
    """Test encoding with Hebrew text."""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_hebrew_text(self, mock_sentence_transformer):
        """Test encoding Hebrew text."""
        mock_model = Mock()
        mock_embedding = np.array([[0.1] * 768])  # 768 dimensions
        mock_model.encode.return_value = mock_embedding
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_sentence_transformer.return_value = mock_model
        
        service = EmbeddingService()
        hebrew_text = "דירה יפה במרכז תל אביב עם 2 חדרים"
        result = service.encode(hebrew_text)
        
        assert result.shape == (768,)
        mock_model.encode.assert_called_once_with(
            hebrew_text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

