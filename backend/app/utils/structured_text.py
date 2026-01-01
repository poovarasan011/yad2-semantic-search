"""
Utilities for generating structured text representations from listings.
Used for creating structured vectors for multivector search.
"""

from typing import Optional
from app.db.models import Listing


def build_structured_text(listing: Listing) -> str:
    """
    Build structured text representation from listing.
    
    Extracts key fields and formats them in Hebrew for embedding.
    Used to generate structured_vector for multivector search.
    
    Args:
        listing: Listing model instance
        
    Returns:
        str: Structured text representation in Hebrew
        
    Example:
        "2 חדרים, תל אביב, דיזינגוף, עם חניה, עם מעלית, מרוהט, 8000 ש״ח"
    """
    parts = []
    
    # Rooms
    if listing.rooms is not None:
        rooms_str = str(float(listing.rooms))
        # Handle .5 rooms (common in Israel)
        if rooms_str.endswith('.0'):
            rooms_str = rooms_str[:-2]
        parts.append(f"{rooms_str} חדרים")
    
    # City
    if listing.city:
        parts.append(listing.city)
    
    # Location/Neighborhood (prefer neighborhood, fallback to location)
    location = listing.neighborhood or listing.location
    if location:
        parts.append(location)
    
    # Features (Hebrew descriptions)
    if listing.has_parking:
        parts.append("עם חניה")
    
    if listing.has_elevator:
        parts.append("עם מעלית")
    
    if listing.furnished:
        parts.append("מרוהט")
    
    if listing.has_balcony:
        parts.append("עם מרפסת")
    
    if listing.has_storage:
        parts.append("עם מחסן")
    
    # Price (optional - only if provided)
    if listing.price is not None:
        parts.append(f"{listing.price:,} ש״ח".replace(",", ","))  # Format with comma separator
    
    # Size (optional)
    if listing.size_sqm:
        parts.append(f"{listing.size_sqm} מ״ר")
    
    # Floor information (optional)
    if listing.floor is not None:
        if listing.floor == 0:
            parts.append("קרקע")
        elif listing.floor < 0:
            parts.append(f"קומה {abs(listing.floor)} למטה")
        else:
            parts.append(f"קומה {listing.floor}")
    
    # Join all parts with comma and space
    structured_text = ", ".join(parts)
    
    # Return empty string if no parts (shouldn't happen, but safety check)
    return structured_text if structured_text else "דירה"

