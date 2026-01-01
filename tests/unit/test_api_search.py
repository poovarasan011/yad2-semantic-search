"""
Unit tests for FastAPI search endpoint.
Tests the search endpoint with mocked dependencies.
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
from app.db.models import Listing


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    mock_db = Mock()
    return mock_db


@pytest.fixture
def client(mock_db_session):
    """Create test client for FastAPI app with mocked dependencies."""
    from app.db.session import get_db
    
    # Override get_db dependency
    def override_get_db():
        try:
            yield mock_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_listing():
    """Create a mock listing object."""
    from datetime import datetime
    listing = Listing(
        id=1,
        external_id="test_001",
        title="דירה יפה",
        description="דירה יפה במרכז תל אביב",
        price=8000,
        rooms=2.0,
        size_sqm=60,
        city="תל אביב",
        location="מרכז",
        neighborhood="דיזינגוף",
        has_parking=False,
        has_elevator=False,
        has_balcony=True,
        has_storage=False,
        furnished=False,
        floor=3,
        total_floors=5,
        pets_allowed=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        scraped_at=datetime.now(),
    )
    return listing


class TestSearchEndpoint:
    """Test search endpoint."""

    @patch("app.api.v1.endpoints.search.search_listings")
    @patch("app.api.v1.endpoints.search.get_listings_by_ids")
    def test_search_success(
        self,
        mock_get_listings,
        mock_search_listings,
        client,
        mock_listing,
        mock_db_session,
    ):
        """Test successful search."""
        # Mock search results
        mock_search_listings.return_value = [(1, 0.95), (2, 0.85)]
        
        # Mock listings retrieval
        mock_get_listings.return_value = [mock_listing]
        
        # Make request
        response = client.get("/api/v1/search", params={"query": "דירה 2 חדרים"})
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "דירה 2 חדרים"
        assert data["total_results"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["listing"]["id"] == 1
        assert data["results"][0]["score"] == 0.95
        assert data["results"][0]["rank"] == 1
        
        # Verify mocks were called
        mock_search_listings.assert_called_once()
        mock_get_listings.assert_called_once()

    @patch("app.api.v1.endpoints.search.search_listings")
    def test_search_no_results(
        self,
        mock_search_listings,
        client,
    ):
        """Test search with no results."""
        # Mock empty search results
        mock_search_listings.return_value = []
        
        # Make request
        response = client.get("/api/v1/search", params={"query": "לא קיים"})
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0
        assert len(data["results"]) == 0

    @patch("app.api.v1.endpoints.search.search_listings")
    def test_search_with_filters(
        self,
        mock_search_listings,
        client,
        mock_listing,
    ):
        """Test search with filters."""
        # Mock search results
        mock_search_listings.return_value = [(1, 0.95)]
        
        # Mock listings retrieval
        with patch("app.api.v1.endpoints.search.get_listings_by_ids") as mock_get_listings:
            mock_get_listings.return_value = [mock_listing]
            
            # Make request with filters
            response = client.get(
                "/api/v1/search",
                params={
                    "query": "דירה",
                    "price_max": 10000,
                    "rooms_min": 2.0,
                    "city": "תל אביב",
                    "has_parking": "false",
                },
            )
            
            # Assertions
            assert response.status_code == 200
            
            # Verify search_listings was called with filters
            call_args = mock_search_listings.call_args
            assert call_args[1]["filters"]["price_max"] == 10000
            assert call_args[1]["filters"]["rooms_min"] == 2.0
            assert call_args[1]["filters"]["city"] == "תל אביב"
            assert call_args[1]["filters"]["has_parking"] is False

    def test_search_missing_query(self, client):
        """Test search without query parameter."""
        response = client.get("/api/v1/search")
        
        assert response.status_code == 422  # Validation error

    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.get("/api/v1/search", params={"query": ""})
        
        assert response.status_code == 422  # Validation error

    def test_search_limit_validation(self, client):
        """Test search limit validation."""
        # Test limit too high
        response = client.get(
            "/api/v1/search",
            params={"query": "דירה", "limit": 200},
        )
        assert response.status_code == 422
        
        # Test limit too low
        response = client.get(
            "/api/v1/search",
            params={"query": "דירה", "limit": 0},
        )
        assert response.status_code == 422

    @patch("app.api.v1.endpoints.search.search_listings")
    def test_search_error_handling(
        self,
        mock_search_listings,
        client,
    ):
        """Test error handling in search endpoint."""
        # Mock search_listings to raise exception
        mock_search_listings.side_effect = Exception("Search failed")
        
        # Make request
        response = client.get("/api/v1/search", params={"query": "דירה"})
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Search failed" in data["detail"]

    @patch("app.api.v1.endpoints.search.search_listings")
    def test_search_limit_parameter(
        self,
        mock_search_listings,
        client,
    ):
        """Test search with custom limit."""
        # Mock search results
        mock_search_listings.return_value = [(i, 0.9 - i * 0.1) for i in range(1, 6)]
        
        # Mock listings retrieval
        with patch("app.api.v1.endpoints.search.get_listings_by_ids") as mock_get_listings:
            from datetime import datetime
            mock_get_listings.return_value = [
                Listing(
                    id=i,
                    external_id=f"test_{i}",
                    description=f"Listing {i}",
                    has_parking=False,
                    has_elevator=False,
                    has_balcony=False,
                    has_storage=False,
                    furnished=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    scraped_at=datetime.now(),
                )
                for i in range(1, 6)
            ]
            
            # Make request with limit
            response = client.get(
                "/api/v1/search",
                params={"query": "דירה", "limit": 5},
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["limit"] == 5
            assert len(data["results"]) <= 5
            
            # Verify limit was passed to search_listings
            call_args = mock_search_listings.call_args
            assert call_args[1]["limit"] == 5

