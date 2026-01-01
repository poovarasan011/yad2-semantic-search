"""
Unit tests for Qdrant utilities.
"""

import pytest
from app.db.models import Listing
from app.utils.qdrant_utils import build_qdrant_payload


class TestQdrantPayloadBuilder:
    """Test Qdrant payload building."""
    
    def test_basic_payload(self):
        """Test payload with basic fields."""
        listing = Listing(
            id=123,
            external_id="yad2_456",
            description="דירה יפה",
            price=8000,
            rooms=2.0,
            city="תל אביב",
        )
        
        payload = build_qdrant_payload(listing)
        
        assert payload["listing_id"] == 123
        assert payload["external_id"] == "yad2_456"
        assert payload["price"] == 8000
        assert payload["rooms"] == 2.0
        assert payload["city"] == "תל אביב"
    
    def test_payload_includes_all_filterable_fields(self):
        """Test payload includes all filterable fields."""
        listing = Listing(
            id=123,
            external_id="yad2_456",
            description="דירה יפה",
            price=8000,
            rooms=3.5,
            size_sqm=90,
            city="תל אביב",
            location="דיזינגוף",
            neighborhood="דיזינגוף",
            floor=3,
            total_floors=5,
            has_parking=True,
            has_elevator=True,
            has_balcony=True,
            has_storage=True,
            furnished=True,
            pets_allowed=True,
        )
        
        payload = build_qdrant_payload(listing)
        
        # Identifiers
        assert "listing_id" in payload
        assert "external_id" in payload
        
        # Numeric fields
        assert "price" in payload
        assert "rooms" in payload
        assert "size_sqm" in payload
        assert "floor" in payload
        assert "total_floors" in payload
        
        # Categorical fields
        assert "city" in payload
        assert "location" in payload
        assert "neighborhood" in payload
        
        # Boolean fields
        assert "has_parking" in payload
        assert "has_elevator" in payload
        assert "has_balcony" in payload
        assert "has_storage" in payload
        assert "furnished" in payload
        assert "pets_allowed" in payload
    
    def test_payload_excludes_none_values(self):
        """Test that None values are excluded from payload."""
        listing = Listing(
            id=123,
            external_id="yad2_456",
            description="דירה יפה",
            price=None,
            rooms=None,
            city=None,
        )
        
        payload = build_qdrant_payload(listing)
        
        # Should not include None values
        assert "price" not in payload
        assert "rooms" not in payload
        assert "city" not in payload
        
        # But should include identifiers and boolean defaults
        assert "listing_id" in payload
        assert "external_id" in payload
        assert "has_parking" in payload  # Boolean defaults to False
    
    def test_payload_boolean_defaults(self):
        """Test that boolean fields always have values."""
        listing = Listing(
            id=123,
            external_id="yad2_456",
            description="דירה יפה",
        )
        
        payload = build_qdrant_payload(listing)
        
        # Booleans should always be present (default False)
        assert payload["has_parking"] is False
        assert payload["has_elevator"] is False
        assert payload["has_balcony"] is False
        assert payload["has_storage"] is False
        assert payload["furnished"] is False
    
    def test_payload_pets_allowed_null(self):
        """Test that pets_allowed can be None (not specified)."""
        listing = Listing(
            id=123,
            external_id="yad2_456",
            description="דירה יפה",
            pets_allowed=None,
        )
        
        payload = build_qdrant_payload(listing)
        
        # pets_allowed should not be in payload if None
        assert "pets_allowed" not in payload
        
        # But should be included if set
        listing.pets_allowed = True
        payload2 = build_qdrant_payload(listing)
        assert "pets_allowed" in payload2
        assert payload2["pets_allowed"] is True
    
    def test_payload_rooms_float_conversion(self):
        """Test that rooms is converted to float."""
        listing = Listing(
            id=123,
            external_id="yad2_456",
            description="דירה יפה",
            rooms=3.5,
        )
        
        payload = build_qdrant_payload(listing)
        
        assert payload["rooms"] == 3.5
        assert isinstance(payload["rooms"], float)


class TestQdrantPointBuilder:
    """Test Qdrant point building with named vectors."""
    
    def test_build_qdrant_point(self):
        """Test building Qdrant point with named vectors."""
        import numpy as np
        from app.utils.qdrant_utils import build_qdrant_point
        
        listing_id = 123
        structured_vec = np.array([0.1, 0.2, 0.3])
        desc_vec = np.array([0.4, 0.5, 0.6])
        payload = {"price": 8000, "city": "תל אביב"}
        
        point = build_qdrant_point(listing_id, structured_vec, desc_vec, payload)
        
        assert point["id"] == 123
        assert "vector" in point
        assert "structured" in point["vector"]
        assert "description" in point["vector"]
        assert point["vector"]["structured"] == [0.1, 0.2, 0.3]
        assert point["vector"]["description"] == [0.4, 0.5, 0.6]
        assert point["payload"] == payload
    
    def test_build_qdrant_point_converts_numpy_to_list(self):
        """Test that numpy arrays are converted to lists."""
        import numpy as np
        from app.utils.qdrant_utils import build_qdrant_point
        
        structured_vec = np.array([0.1, 0.2, 0.3])
        desc_vec = np.array([0.4, 0.5, 0.6])
        
        point = build_qdrant_point(1, structured_vec, desc_vec, {})
        
        # Should be lists, not numpy arrays
        assert isinstance(point["vector"]["structured"], list)
        assert isinstance(point["vector"]["description"], list)

