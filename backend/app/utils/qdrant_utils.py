"""
Utilities for Qdrant operations.
Helper functions for building payloads and managing Qdrant data structures.
"""

from typing import Dict, Any, Optional, List
import numpy as np
from app.db.models import Listing


def build_qdrant_payload(listing: Listing) -> Dict[str, Any]:
    """
    Build Qdrant payload with filterable fields and identifiers.
    
    Payload contains only fields needed for filtering during search.
    Full data remains in PostgreSQL (source of truth).
    
    Args:
        listing: Listing model instance
        
    Returns:
        dict: Payload dictionary with filterable fields
    """
    payload: Dict[str, Any] = {
        # Identifiers for mapping back to PostgreSQL
        "listing_id": listing.id,
        "external_id": listing.external_id,
    }
    
    # Filterable numeric fields
    if listing.price is not None:
        payload["price"] = listing.price
    
    if listing.rooms is not None:
        payload["rooms"] = float(listing.rooms)
    
    if listing.size_sqm is not None:
        payload["size_sqm"] = listing.size_sqm
    
    if listing.floor is not None:
        payload["floor"] = listing.floor
    
    if listing.total_floors is not None:
        payload["total_floors"] = listing.total_floors
    
    # Filterable categorical fields
    if listing.city:
        payload["city"] = listing.city
    
    if listing.location:
        payload["location"] = listing.location
    
    if listing.neighborhood:
        payload["neighborhood"] = listing.neighborhood
    
    # Boolean flags (for filtering) - always include, default to False
    payload["has_parking"] = listing.has_parking if listing.has_parking is not None else False
    payload["has_elevator"] = listing.has_elevator if listing.has_elevator is not None else False
    payload["has_balcony"] = listing.has_balcony if listing.has_balcony is not None else False
    payload["has_storage"] = listing.has_storage if listing.has_storage is not None else False
    payload["furnished"] = listing.furnished if listing.furnished is not None else False
    
    # pets_allowed can be None (not specified)
    if listing.pets_allowed is not None:
        payload["pets_allowed"] = listing.pets_allowed
    
    return payload


def build_qdrant_point(
    listing_id: int,
    structured_vector: np.ndarray,
    description_vector: np.ndarray,
    payload: Dict[str, Any],
) -> Dict:
    """
    Build Qdrant point structure with named vectors.
    
    Uses named vectors approach:
    - "structured" vector for structured text embedding
    - "description" vector for description text embedding
    
    Args:
        listing_id: Listing ID (used as point ID)
        structured_vector: Vector embedding of structured text (numpy array)
        description_vector: Vector embedding of description (numpy array)
        payload: Payload dictionary from build_qdrant_payload()
        
    Returns:
        dict: Point structure ready for Qdrant upsert
        
    Example:
        point_dict = build_qdrant_point(
            listing_id=123,
            structured_vector=structured_vec,
            description_vector=desc_vec,
            payload=payload
        )
        # Use with: qdrant_client.upsert(points=[PointStruct(**point_dict)])
    """
    # Convert numpy arrays to lists for JSON serialization
    return {
        "id": listing_id,
        "vector": {
            "structured": structured_vector.tolist() if isinstance(structured_vector, np.ndarray) else structured_vector,
            "description": description_vector.tolist() if isinstance(description_vector, np.ndarray) else description_vector,
        },
        "payload": payload,
    }

