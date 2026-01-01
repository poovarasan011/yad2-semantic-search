"""
Unit tests for FastAPI ingest endpoint.
Tests the ingest endpoint with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


class TestIngestEndpoint:
    """Test ingest endpoint."""

    @patch("app.api.v1.endpoints.ingest.run_etl_pipeline")
    def test_ingest_success(self, mock_run_etl_pipeline, client):
        """Test successful ingest trigger."""
        # Mock the ETL pipeline function to avoid actually running it
        mock_run_etl_pipeline.return_value = {"status": "success"}
        
        # Make request
        response = client.post("/api/v1/ingest")
        
        # Assertions - endpoint should accept the request and return immediately
        # Background task execution is tested in integration tests
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert "message" in data
        message_lower = data["message"].lower()
        assert "etl pipeline" in message_lower and "started" in message_lower

