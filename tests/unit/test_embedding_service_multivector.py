"""
Unit tests for multivector encoding functionality in embedding service.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.db.models import Listing
from app.services.embedding_service import EmbeddingService


@pytest.fixture(autouse=True)
def reset_embedding_service():
    """Reset the singleton instance before each test."""
    EmbeddingService._instance = None
    EmbeddingService._model = None
    
    import app.services.embedding_service as embedding_module
    embedding_module._embedding_service = None
    
    yield
    
    EmbeddingService._instance = None
    EmbeddingService._model = None
    embedding_module._embedding_service = None


class TestEmbeddingServiceMultivector:
    """Test multivector encoding methods."""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_listing_returns_two_vectors(self, mock_sentence_transformer):
        """Test that encode_listing returns two vectors."""
        # Setup mock model
        mock_model = Mock()
        
        # Mock encode to return different vectors for structured and description
        structured_vec = np.array([0.1, 0.2, 0.3, 0.4])
        desc_vec = np.array([0.5, 0.6, 0.7, 0.8])
        mock_model.encode.side_effect = [
            structured_vec.reshape(1, -1),  # First call (structured)
            desc_vec.reshape(1, -1),        # Second call (description)
        ]
        mock_model.get_sentence_embedding_dimension.return_value = 4
        mock_sentence_transformer.return_value = mock_model
        
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה במרכז תל אביב",
            rooms=2.0,
            city="תל אביב",
        )
        
        service = EmbeddingService()
        structured_vector, description_vector = service.encode_listing(listing)
        
        # Should return two vectors
        assert isinstance(structured_vector, np.ndarray)
        assert isinstance(description_vector, np.ndarray)
        assert structured_vector.shape == (4,)
        assert description_vector.shape == (4,)
        
        # Should call encode twice (structured + description)
        assert mock_model.encode.call_count == 2
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_listing_empty_description_raises_error(self, mock_sentence_transformer):
        """Test that encode_listing raises error for empty description."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="",  # Empty description
        )
        
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="Listing description cannot be empty"):
            service.encode_listing(listing)
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_listings_batch(self, mock_sentence_transformer):
        """Test batch encoding of listings."""
        # Setup mock model
        mock_model = Mock()
        
        # Mock batch encode to return arrays
        mock_structured_vecs = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        mock_desc_vecs = np.array([
            [0.7, 0.8, 0.9],
            [1.0, 1.1, 1.2],
        ])
        mock_model.encode.side_effect = [mock_structured_vecs, mock_desc_vecs]
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_sentence_transformer.return_value = mock_model
        
        listings = [
            Listing(
                id=1,
                external_id="test_1",
                description="דירה יפה",
                rooms=2.0,
            ),
            Listing(
                id=2,
                external_id="test_2",
                description="בית גדול",
                rooms=3.0,
            ),
        ]
        
        service = EmbeddingService()
        results = service.encode_listings_batch(listings)
        
        # Should return list of tuples
        assert len(results) == 2
        assert isinstance(results[0], tuple)
        assert len(results[0]) == 2  # (structured_vec, desc_vec)
        
        # Check vectors have correct shape
        assert results[0][0].shape == (3,)
        assert results[0][1].shape == (3,)
        
        # Should call encode_batch twice (structured + descriptions)
        assert mock_model.encode.call_count == 2
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_listings_batch_empty_list_raises_error(self, mock_sentence_transformer):
        """Test that encode_listings_batch raises error for empty list."""
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="Listings list cannot be empty"):
            service.encode_listings_batch([])
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_encode_listing_uses_structured_text_generator(self, mock_sentence_transformer):
        """Test that encode_listing uses structured text generator."""
        mock_model = Mock()
        mock_vec = np.array([[0.1, 0.2, 0.3]])
        mock_model.encode.return_value = mock_vec
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_sentence_transformer.return_value = mock_model
        
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            rooms=2.0,
            city="תל אביב",
            has_parking=True,
        )
        
        service = EmbeddingService()
        service.encode_listing(listing)
        
        # Check that encode was called with structured text (should contain fields)
        call_args_list = mock_model.encode.call_args_list
        assert len(call_args_list) == 2
        
        # First call should be structured text (should contain room/city info)
        structured_text = call_args_list[0][0][0]  # First positional arg
        assert "2 חדרים" in structured_text or "תל אביב" in structured_text or "עם חניה" in structured_text
        
        # Second call should be description
        description = call_args_list[1][0][0]
        assert description == "דירה יפה"

