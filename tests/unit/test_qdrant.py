"""
Unit tests for Qdrant client and collection management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from qdrant_client.models import CollectionStatus
from app.db.qdrant import QdrantManager, init_qdrant, get_qdrant_client
from app.core.config import settings


class TestQdrantManager:
    """Test cases for QdrantManager."""
    
    def test_qdrant_manager_initialization(self):
        """Test QdrantManager initialization."""
        manager = QdrantManager()
        assert manager.client is None
        assert manager.collection_name == settings.QDRANT_COLLECTION_NAME
        assert manager.vector_size == settings.QDRANT_VECTOR_SIZE
    
    @patch('app.db.qdrant.QdrantClient')
    def test_qdrant_connect(self, mock_qdrant_client_class):
        """Test connecting to Qdrant."""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        client = manager.connect()
        
        assert client is not None
        assert manager.client is not None
        mock_qdrant_client_class.assert_called_once()
    
    @patch('app.db.qdrant.QdrantClient')
    def test_qdrant_connect_reuses_connection(self, mock_qdrant_client_class):
        """Test that connect reuses existing connection."""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        client1 = manager.connect()
        client2 = manager.connect()
        
        assert client1 is client2
        # Should only create client once
        assert mock_qdrant_client_class.call_count == 1
    
    @patch('app.db.qdrant.QdrantClient')
    def test_ensure_collection_exists_creates_new(self, mock_qdrant_client_class):
        """Test creating collection when it doesn't exist."""
        mock_client = Mock()
        mock_collections_response = Mock()
        mock_collections_response.collections = []  # No collections
        mock_client.get_collections.return_value = mock_collections_response
        mock_client.get_collection.return_value = Mock(status=CollectionStatus.GREEN)
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        manager.connect()
        manager.ensure_collection_exists()
        
        # Should create collection
        mock_client.create_collection.assert_called_once()
    
    @patch('app.db.qdrant.QdrantClient')
    def test_ensure_collection_exists_skips_existing(self, mock_qdrant_client_class):
        """Test skipping collection creation when it exists."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.name = settings.QDRANT_COLLECTION_NAME
        mock_collections_response = Mock()
        mock_collections_response.collections = [mock_collection]
        mock_client.get_collections.return_value = mock_collections_response
        mock_client.get_collection.return_value = Mock(status=CollectionStatus.GREEN)
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        manager.connect()
        manager.ensure_collection_exists()
        
        # Should not create collection
        mock_client.create_collection.assert_not_called()
    
    @patch('app.db.qdrant.QdrantClient')
    def test_get_collection_info(self, mock_qdrant_client_class):
        """Test getting collection information."""
        mock_client = Mock()
        mock_info = Mock()
        mock_info.config.params.vectors.size = 768
        mock_info.points_count = 100
        mock_info.status = CollectionStatus.GREEN
        mock_client.get_collection.return_value = mock_info
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        manager.connect()
        info = manager.get_collection_info()
        
        assert "vector_size" in info
        assert "points_count" in info
        assert "status" in info
    
    @patch('app.db.qdrant.QdrantClient')
    def test_health_check_success(self, mock_qdrant_client_class):
        """Test successful health check."""
        mock_client = Mock()
        mock_client.get_collections.return_value = Mock()
        mock_qdrant_client_class.return_value = mock_client
        
        manager = QdrantManager()
        manager.connect()
        is_healthy = manager.health_check()
        
        assert is_healthy is True
    
    @patch('app.db.qdrant.QdrantClient')
    def test_health_check_failure(self, mock_qdrant_client_class):
        """Test failed health check."""
        mock_qdrant_client_class.side_effect = Exception("Connection failed")
        
        manager = QdrantManager()
        is_healthy = manager.health_check()
        
        assert is_healthy is False


class TestQdrantFunctions:
    """Test cases for Qdrant module functions."""
    
    @patch('app.db.qdrant.qdrant_manager')
    def test_init_qdrant(self, mock_manager):
        """Test Qdrant initialization."""
        init_qdrant()
        mock_manager.connect.assert_called_once()
        mock_manager.ensure_collection_exists.assert_called_once()
    
    @patch('app.db.qdrant.qdrant_manager')
    def test_get_qdrant_client(self, mock_manager):
        """Test getting Qdrant client."""
        mock_client = Mock()
        mock_manager.connect.return_value = mock_client
        
        client = get_qdrant_client()
        
        assert client is mock_client
        mock_manager.connect.assert_called_once()

