"""
Vectorization processor for generating embeddings.
Wraps the embedding service for use in ETL pipeline.
"""

import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.embedding_service import get_embedding_service
from app.utils.structured_text import build_structured_text
from app.db.models import Listing


def generate_listing_embeddings(listing: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate embeddings for a single listing.
    
    Creates both structured and description vectors for multivector search.
    
    Args:
        listing: Listing dictionary with all fields
        
    Returns:
        Tuple of (structured_vector, description_vector)
    """
    embedding_service = get_embedding_service()
    
    # Create temporary Listing object for structured text generation
    class TempListing:
        def __init__(self, data):
            self.id = data.get("id")
            self.description = data.get("description", "")
            self.rooms = data.get("rooms")
            self.city = data.get("city")
            self.location = data.get("location")
            self.neighborhood = data.get("neighborhood")
            self.has_parking = data.get("has_parking", False)
            self.has_elevator = data.get("has_elevator", False)
            self.has_balcony = data.get("has_balcony", False)
            self.has_storage = data.get("has_storage", False)
            self.furnished = data.get("furnished", False)
            self.price = data.get("price")
            self.size_sqm = data.get("size_sqm")
            self.floor = data.get("floor")
            self.total_floors = data.get("total_floors")
    
    temp_listing = TempListing(listing)
    
    # Generate structured text
    structured_text = build_structured_text(temp_listing)
    
    # Encode structured text
    structured_vector = embedding_service.encode(structured_text)
    
    # Encode description
    description = listing.get("description", "")
    if not description:
        raise ValueError(f"Listing {listing.get('external_id')} has empty description")
    description_vector = embedding_service.encode(description)
    
    return structured_vector, description_vector


def generate_listings_embeddings_batch(
    listings: List[Dict[str, Any]],
    show_progress: bool = True,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Generate embeddings for multiple listings efficiently using batch processing.
    
    Args:
        listings: List of listing dictionaries
        show_progress: Whether to show progress bar
        
    Returns:
        List of tuples: [(structured_vec, desc_vec), ...]
    """
    embedding_service = get_embedding_service()
    
    # Create temporary Listing objects
    class TempListing:
        def __init__(self, data):
            self.id = data.get("id")
            self.description = data.get("description", "")
            self.rooms = data.get("rooms")
            self.city = data.get("city")
            self.location = data.get("location")
            self.neighborhood = data.get("neighborhood")
            self.has_parking = data.get("has_parking", False)
            self.has_elevator = data.get("has_elevator", False)
            self.has_balcony = data.get("has_balcony", False)
            self.has_storage = data.get("has_storage", False)
            self.furnished = data.get("furnished", False)
            self.price = data.get("price")
            self.size_sqm = data.get("size_sqm")
            self.floor = data.get("floor")
            self.total_floors = data.get("total_floors")
    
    temp_listings = [TempListing(listing) for listing in listings]
    
    # Build structured texts
    structured_texts = [build_structured_text(listing) for listing in temp_listings]
    descriptions = [listing.description for listing in temp_listings]
    
    # Batch encode
    structured_vectors = embedding_service.encode_batch(structured_texts, show_progress=show_progress)
    description_vectors = embedding_service.encode_batch(descriptions, show_progress=show_progress)
    
    # Pair them up
    result = [
        (structured_vectors[i], description_vectors[i])
        for i in range(len(listings))
    ]
    
    return result
