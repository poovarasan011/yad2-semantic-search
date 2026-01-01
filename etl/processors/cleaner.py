"""
Data cleaning processor for apartment listings.
Handles text normalization and Hebrew-specific cleaning.
"""

import re
from typing import Dict, List, Any
import html


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def clean_listing(listing: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean a single listing dictionary.
    
    Args:
        listing: Raw listing data dictionary
        
    Returns:
        Cleaned listing dictionary
    """
    cleaned = listing.copy()
    
    # Clean text fields
    if "title" in cleaned and cleaned["title"]:
        cleaned["title"] = clean_text(cleaned["title"])
    
    if "description" in cleaned and cleaned["description"]:
        cleaned["description"] = clean_text(cleaned["description"])
    
    if "location" in cleaned and cleaned["location"]:
        cleaned["location"] = clean_text(cleaned["location"])
    
    if "neighborhood" in cleaned and cleaned["neighborhood"]:
        cleaned["neighborhood"] = clean_text(cleaned["neighborhood"])
    
    if "city" in cleaned and cleaned["city"]:
        cleaned["city"] = clean_text(cleaned["city"])
    
    # Normalize numeric fields
    if "price" in cleaned and cleaned["price"]:
        # Remove currency symbols and commas, keep only digits
        price_str = str(cleaned["price"]).replace(",", "").replace("ש״ח", "").strip()
        try:
            cleaned["price"] = int(price_str)
        except (ValueError, TypeError):
            cleaned["price"] = None
    
    if "rooms" in cleaned and cleaned["rooms"]:
        try:
            cleaned["rooms"] = float(cleaned["rooms"])
        except (ValueError, TypeError):
            cleaned["rooms"] = None
    
    if "size_sqm" in cleaned and cleaned["size_sqm"]:
        try:
            cleaned["size_sqm"] = int(cleaned["size_sqm"])
        except (ValueError, TypeError):
            cleaned["size_sqm"] = None
    
    # Ensure boolean fields are proper booleans
    for bool_field in ["has_parking", "has_elevator", "has_balcony", "has_storage", "furnished"]:
        if bool_field in cleaned:
            if cleaned[bool_field] is None:
                cleaned[bool_field] = False
            else:
                cleaned[bool_field] = bool(cleaned[bool_field])
    
    return cleaned


def clean_listings(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean a batch of listings.
    
    Args:
        listings: List of raw listing dictionaries
        
    Returns:
        List of cleaned listing dictionaries
    """
    return [clean_listing(listing) for listing in listings]
