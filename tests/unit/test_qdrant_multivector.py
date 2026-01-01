"""
Unit tests for Qdrant named vectors configuration.
"""

import pytest
from unittest.mock import Mock, patch
from app.db.qdrant import QdrantManager


class TestQdrantNamedVectorsConfig:
    """Test named vectors configuration in Qdrant."""
    
    @patch('app.db.qdrant.QdrantClient')
    def test_collection_created_with_named_vectors(self, mock_qdrant_client_class):
        """Test that collection is created with named vectors config."""
        mock_client = Mock()
        mock_collections_response = Mock()
        mock_collections_response.collections = []  # No collections
        mock_client.get_collections.return_value = mock_collections_response
        mock_client.get_collection.return_value = Mock(status=Mock(value="green"))
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        manager.connect()
        manager.ensure_collection_exists()
        
        # Check that create_collection was called
        assert mock_client.create_collection.called
        
        # Get vectors_config from call
        create_call = mock_client.create_collection.call_args
        vectors_config = create_call.kwargs.get("vectors_config")
        
        # Should be a dictionary with named vectors
        assert isinstance(vectors_config, dict)
        assert "structured" in vectors_config
        assert "description" in vectors_config

