"""
Qdrant loader for batch upserting vectors.
Handles batch upserts with named vectors (structured + description).
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.db.qdrant import get_qdrant_client
from app.utils.qdrant_utils import build_qdrant_payload, build_qdrant_point
from app.db.models import Listing


def load_vectors_to_qdrant(
    listings: List[Dict[str, Any]],
    embeddings: List[Tuple[np.ndarray, np.ndarray]],
    client: Optional[QdrantClient] = None,
    collection_name: str = "apartments",
    batch_size: int = 100,
) -> Dict[str, int]:
    """
    Load vectors into Qdrant vector database.
    
    Args:
        listings: List of listing dictionaries (must match embeddings order)
        embeddings: List of (structured_vector, description_vector) tuples
        client: Optional Qdrant client (creates new if not provided)
        collection_name: Qdrant collection name
        batch_size: Number of points to upsert per batch
        
    Returns:
        Dictionary with counts: {"loaded": int, "errors": int}
    """
    if len(listings) != len(embeddings):
        raise ValueError(f"Mismatch: {len(listings)} listings but {len(embeddings)} embeddings")
    
    if not listings:
        return {"loaded": 0, "errors": 0}
    
    if client is None:
        client = get_qdrant_client()
    
    loaded_count = 0
    error_count = 0
    
    try:
        # Process in batches
        for i in range(0, len(listings), batch_size):
            batch_listings = listings[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            try:
                points = []
                
                for listing, (structured_vec, desc_vec) in zip(batch_listings, batch_embeddings):
                    # Get listing ID (must be database ID from PostgreSQL)
                    listing_id = listing.get("id")
                    if not listing_id:
                        raise ValueError(
                            f"Listing {listing.get('external_id')} missing database ID. "
                            "Ensure PostgreSQL loader runs before Qdrant loader."
                        )
                    
                    # Create temporary Listing object for payload building
                    class TempListing:
                        def __init__(self, data):
                            self.id = listing_id
                            self.external_id = data.get("external_id", str(listing_id))
                            self.price = data.get("price")
                            self.rooms = data.get("rooms")
                            self.size_sqm = data.get("size_sqm")
                            self.city = data.get("city")
                            self.location = data.get("location")
                            self.neighborhood = data.get("neighborhood")
                            self.floor = data.get("floor")
                            self.total_floors = data.get("total_floors")
                            self.has_parking = data.get("has_parking", False)
                            self.has_elevator = data.get("has_elevator", False)
                            self.has_balcony = data.get("has_balcony", False)
                            self.has_storage = data.get("has_storage", False)
                            self.furnished = data.get("furnished", False)
                            self.pets_allowed = data.get("pets_allowed")
                    
                    temp_listing = TempListing(listing)
                    
                    # Build payload
                    payload = build_qdrant_payload(temp_listing)
                    
                    # Build point with named vectors
                    point_dict = build_qdrant_point(
                        listing_id=listing_id,
                        structured_vector=structured_vec,
                        description_vector=desc_vec,
                        payload=payload,
                    )
                    
                    # Convert to PointStruct
                    point = PointStruct(
                        id=point_dict["id"],
                        vector=point_dict["vector"],
                        payload=point_dict["payload"],
                    )
                    points.append(point)
                
                if not points:
                    continue
                
                # Upsert batch
                client.upsert(
                    collection_name=collection_name,
                    points=points,
                    wait=True,  # Wait for indexing
                )
                
                loaded_count += len(points)
                
            except Exception as e:
                error_count += len(batch_listings)
                print(f"Error loading batch {i//batch_size + 1} to Qdrant: {e}")
                continue
        
        return {
            "loaded": loaded_count,
            "errors": error_count,
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to load vectors to Qdrant: {e}") from e
