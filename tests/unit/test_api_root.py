"""
Unit tests for FastAPI root and health endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns app info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


class TestHealthEndpoint:
    """Test health check endpoint."""

    @patch("sqlalchemy.create_engine")
    @patch("app.db.qdrant.qdrant_manager")
    def test_health_check_success(
        self,
        mock_qdrant_manager,
        mock_create_engine,
        client,
    ):
        """Test health check when all services are healthy."""
        
        # Mock Qdrant health check
        mock_qdrant_manager.health_check.return_value = True
        
        # Mock PostgreSQL connection
        mock_engine = Mock()
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_engine.connect.return_value = mock_conn
        mock_create_engine.return_value = mock_engine
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["qdrant"] == "healthy"
        assert data["postgresql"] == "healthy"

    @patch("sqlalchemy.create_engine")
    @patch("app.db.qdrant.qdrant_manager")
    def test_health_check_qdrant_unhealthy(
        self,
        mock_qdrant_manager,
        mock_create_engine,
        client,
    ):
        """Test health check when Qdrant is unhealthy."""
        
        # Mock Qdrant health check to fail
        mock_qdrant_manager.health_check.return_value = False
        
        # Mock PostgreSQL connection
        mock_engine = Mock()
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_engine.connect.return_value = mock_conn
        mock_create_engine.return_value = mock_engine
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["qdrant"] == "unhealthy"
        assert data["postgresql"] == "healthy"

    @patch("sqlalchemy.create_engine")
    @patch("app.db.qdrant.qdrant_manager")
    def test_health_check_postgres_unhealthy(
        self,
        mock_qdrant_manager,
        mock_create_engine,
        client,
    ):
        """Test health check when PostgreSQL is unhealthy."""
        
        # Mock Qdrant health check
        mock_qdrant_manager.health_check.return_value = True
        
        # Mock PostgreSQL connection failure
        mock_engine = Mock()
        mock_engine.connect.side_effect = Exception("Connection failed")
        mock_create_engine.return_value = mock_engine
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["qdrant"] == "healthy"
        assert data["postgresql"] == "unhealthy"

