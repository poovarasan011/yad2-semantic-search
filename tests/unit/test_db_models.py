"""
Unit tests for database models.
"""

import pytest
from datetime import datetime
from app.db.models import Listing


class TestListingModel:
    """Test cases for the Listing model."""
    
    def test_listing_creation(self, test_db_session):
        """Test creating a listing with all fields."""
        listing = Listing(
            external_id="yad2_12345",
            title="דירה יפה במרכז תל אביב",
            description="דירת 2 חדרים במרכז תל אביב, קרוב לדיזינגוף",
            price=8000,
            rooms=2.0,
            size_sqm=60,
            city="תל אביב",
            location="דיזינגוף",
            neighborhood="דיזינגוף",
            floor=3,
            total_floors=5,
            has_parking=True,
            has_elevator=True,
            has_balcony=True,
            furnished=False,
        )
        
        test_db_session.add(listing)
        test_db_session.commit()
        
        assert listing.id is not None
        assert listing.external_id == "yad2_12345"
        assert listing.price == 8000
        assert float(listing.rooms) == 2.0
        assert listing.city == "תל אביב"
    
    def test_listing_minimal_fields(self, test_db_session):
        """Test creating a listing with only required fields."""
        listing = Listing(
            external_id="yad2_67890",
            description="דירה יפה",
        )
        
        test_db_session.add(listing)
        test_db_session.commit()
        
        assert listing.id is not None
        assert listing.external_id == "yad2_67890"
        assert listing.description == "דירה יפה"
        assert listing.price is None
        assert listing.rooms is None
    
    def test_listing_unique_external_id(self, test_db_session):
        """Test that external_id must be unique."""
        listing1 = Listing(
            external_id="yad2_unique",
            description="First listing",
        )
        test_db_session.add(listing1)
        test_db_session.commit()
        
        listing2 = Listing(
            external_id="yad2_unique",  # Duplicate
            description="Second listing",
        )
        test_db_session.add(listing2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_db_session.commit()
    
    def test_listing_to_dict(self, test_db_session):
        """Test converting listing to dictionary."""
        listing = Listing(
            external_id="yad2_dict_test",
            description="Test description",
            price=5000,
            rooms=3.5,
            city="ירושלים",
        )
        test_db_session.add(listing)
        test_db_session.commit()
        
        result = listing.to_dict()
        
        assert isinstance(result, dict)
        assert result["external_id"] == "yad2_dict_test"
        assert result["price"] == 5000
        assert result["rooms"] == 3.5
        assert result["city"] == "ירושלים"
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_listing_boolean_defaults(self, test_db_session):
        """Test that boolean fields have correct defaults."""
        listing = Listing(
            external_id="yad2_defaults",
            description="Test",
        )
        
        # SQLAlchemy defaults are applied when object is added to session
        test_db_session.add(listing)
        test_db_session.flush()  # Flush to apply defaults
        
        assert listing.has_parking is False
        assert listing.has_elevator is False
        assert listing.has_balcony is False
        assert listing.has_storage is False
        assert listing.furnished is False
        assert listing.pets_allowed is None  # Can be None
    
    def test_listing_repr(self, test_db_session):
        """Test string representation of listing."""
        listing = Listing(
            external_id="yad2_repr",
            description="Test",
            city="תל אביב",
            rooms=2.0,
            price=6000,
        )
        
        repr_str = repr(listing)
        assert "yad2_repr" in repr_str
        assert "תל אביב" in repr_str or "Listing" in repr_str

