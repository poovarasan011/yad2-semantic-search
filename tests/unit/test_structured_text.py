"""
Unit tests for structured text generation.
"""

import pytest
from app.db.models import Listing
from app.utils.structured_text import build_structured_text


class TestStructuredTextGeneration:
    """Test structured text generation from listings."""
    
    def test_basic_structured_text(self):
        """Test generating structured text with basic fields."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            rooms=2.0,
            city="תל אביב",
            neighborhood="דיזינגוף",
        )
        
        result = build_structured_text(listing)
        
        assert "2 חדרים" in result
        assert "תל אביב" in result
        assert "דיזינגוף" in result
    
    def test_structured_text_with_features(self):
        """Test structured text includes features."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            rooms=3.5,
            city="ירושלים",
            has_parking=True,
            has_elevator=True,
            furnished=True,
        )
        
        result = build_structured_text(listing)
        
        assert "3.5 חדרים" in result
        assert "ירושלים" in result
        assert "עם חניה" in result
        assert "עם מעלית" in result
        assert "מרוהט" in result
    
    def test_structured_text_with_price(self):
        """Test structured text includes price."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            price=8000,
            rooms=2.0,
        )
        
        result = build_structured_text(listing)
        
        assert "8,000 ש״ח" in result
    
    def test_structured_text_with_size(self):
        """Test structured text includes size."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            size_sqm=60,
            rooms=2.0,
        )
        
        result = build_structured_text(listing)
        
        assert "60 מ״ר" in result
    
    def test_structured_text_with_floor(self):
        """Test structured text includes floor information."""
        # Ground floor
        listing1 = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            floor=0,
        )
        result1 = build_structured_text(listing1)
        assert "קרקע" in result1
        
        # Regular floor
        listing2 = Listing(
            id=2,
            external_id="test_2",
            description="דירה יפה",
            floor=3,
        )
        result2 = build_structured_text(listing2)
        assert "קומה 3" in result2
        
        # Basement
        listing3 = Listing(
            id=3,
            external_id="test_3",
            description="דירה יפה",
            floor=-1,
        )
        result3 = build_structured_text(listing3)
        assert "קומה 1 למטה" in result3
    
    def test_structured_text_prefers_neighborhood_over_location(self):
        """Test that neighborhood is preferred over location."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            location="מיקום כללי",
            neighborhood="שכונה ספציפית",
        )
        
        result = build_structured_text(listing)
        
        assert "שכונה ספציפית" in result
        assert "מיקום כללי" not in result
    
    def test_structured_text_fallback_to_location(self):
        """Test fallback to location when neighborhood is missing."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            location="מיקום כללי",
            neighborhood=None,
        )
        
        result = build_structured_text(listing)
        
        assert "מיקום כללי" in result
    
    def test_structured_text_all_features(self):
        """Test structured text with all features."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה יפה",
            rooms=4.5,
            city="תל אביב",
            neighborhood="דיזינגוף",
            price=10000,
            size_sqm=120,
            floor=5,
            has_parking=True,
            has_elevator=True,
            has_balcony=True,
            has_storage=True,
            furnished=True,
        )
        
        result = build_structured_text(listing)
        
        # Check all fields are present
        assert "4.5 חדרים" in result
        assert "תל אביב" in result
        assert "דיזינגוף" in result
        assert "10,000 ש״ח" in result
        assert "120 מ״ר" in result
        assert "קומה 5" in result
        assert "עם חניה" in result
        assert "עם מעלית" in result
        assert "עם מרפסת" in result
        assert "עם מחסן" in result
        assert "מרוהט" in result
    
    def test_structured_text_minimal_listing(self):
        """Test structured text with minimal listing data."""
        listing = Listing(
            id=1,
            external_id="test_1",
            description="דירה",
        )
        
        result = build_structured_text(listing)
        
        # Should return at least something (falls back to "דירה")
        assert len(result) > 0
        assert isinstance(result, str)
    
    def test_structured_text_room_formatting(self):
        """Test room number formatting (handles .0 and .5)."""
        # Integer rooms
        listing1 = Listing(
            id=1,
            external_id="test_1",
            description="דירה",
            rooms=2.0,
        )
        result1 = build_structured_text(listing1)
        assert "2 חדרים" in result1
        
        # Half rooms
        listing2 = Listing(
            id=2,
            external_id="test_2",
            description="דירה",
            rooms=3.5,
        )
        result2 = build_structured_text(listing2)
        assert "3.5 חדרים" in result2

