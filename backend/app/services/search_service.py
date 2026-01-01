"""
Search service for semantic search functionality.
Handles query embedding, vector search, and result ranking.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# Add backend to path for imports (if needed)
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter, 
    FieldCondition, 
    Range, 
    MatchValue,
)
from sqlalchemy.orm import Session

from app.services.embedding_service import get_embedding_service
from app.db.qdrant import get_qdrant_client
from app.db.session import get_db
from app.db.models import Listing
from app.core.config import settings

logger = logging.getLogger(__name__)


def build_qdrant_filter(search_request: Dict[str, Any]) -> Optional[Filter]:
    """
    Build Qdrant filter from search request parameters.
    
    Args:
        search_request: Dictionary with filter parameters
        
    Returns:
        Qdrant Filter object or None if no filters
    """
    conditions = []
    
    # Price range
    if search_request.get("price_min") is not None or search_request.get("price_max") is not None:
        price_range = {}
        if search_request.get("price_min") is not None:
            price_range["gte"] = search_request["price_min"]
        if search_request.get("price_max") is not None:
            price_range["lte"] = search_request["price_max"]
        
        if price_range:
            conditions.append(
                FieldCondition(key="price", range=Range(**price_range))
            )
    
    # Rooms range
    if search_request.get("rooms_min") is not None or search_request.get("rooms_max") is not None:
        rooms_range = {}
        if search_request.get("rooms_min") is not None:
            rooms_range["gte"] = search_request["rooms_min"]
        if search_request.get("rooms_max") is not None:
            rooms_range["lte"] = search_request["rooms_max"]
        
        if rooms_range:
            conditions.append(
                FieldCondition(key="rooms", range=Range(**rooms_range))
            )
    
    # City filter
    if search_request.get("city"):
        conditions.append(
            FieldCondition(key="city", match=MatchValue(value=search_request["city"]))
        )
    
    # Location filter
    if search_request.get("location"):
        conditions.append(
            FieldCondition(key="location", match=MatchValue(value=search_request["location"]))
        )
    
    # Boolean filters
    if search_request.get("has_parking") is not None:
        conditions.append(
            FieldCondition(key="has_parking", match=MatchValue(value=search_request["has_parking"]))
        )
    
    if search_request.get("has_elevator") is not None:
        conditions.append(
            FieldCondition(key="has_elevator", match=MatchValue(value=search_request["has_elevator"]))
        )
    
    if search_request.get("furnished") is not None:
        conditions.append(
            FieldCondition(key="furnished", match=MatchValue(value=search_request["furnished"]))
        )
    
    if not conditions:
        return None
    
    return Filter(must=conditions)


def search_listings(
    query: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    qdrant_client: Optional[QdrantClient] = None,
) -> List[Tuple[int, float]]:
    """
    Perform semantic search on listings using multivector approach.
    
    Searches both structured and description vectors, then combines results
    using MAX_SIM strategy (takes maximum similarity from both).
    
    Args:
        query: Search query text (Hebrew)
        limit: Maximum number of results
        filters: Optional filter dictionary
        qdrant_client: Optional Qdrant client (creates new if not provided)
        
    Returns:
        List of tuples: [(listing_id, similarity_score), ...] sorted by score descending
    """
    if qdrant_client is None:
        qdrant_client = get_qdrant_client()
    
    # Encode query
    embedding_service = get_embedding_service()
    query_vector = embedding_service.encode(query)
    
    # Build filter
    qdrant_filter = None
    if filters:
        qdrant_filter = build_qdrant_filter(filters)
    
    try:
        # Search both structured and description vectors
        # For named vectors, we search both and combine results using MAX_SIM strategy
        # Use query_points with 'using' parameter to specify named vector
        
        # Search structured vector
        structured_response = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_vector.tolist(),
            using="structured",  # Named vector name
            query_filter=qdrant_filter,
            limit=limit * 2,  # Get more candidates for combining
        )
        structured_results = structured_response.points
        
        # Search description vector
        description_response = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_vector.tolist(),
            using="description",  # Named vector name
            query_filter=qdrant_filter,
            limit=limit * 2,  # Get more candidates for combining
        )
        description_results = description_response.points
        
        # Combine results: take maximum score for each listing ID (MAX_SIM strategy)
        scores_by_id: Dict[int, float] = {}
        
        # Process structured results (query_points returns QueryResponse with points)
        for point in structured_results:
            listing_id = point.id
            score = point.score
            if listing_id not in scores_by_id or score > scores_by_id[listing_id]:
                scores_by_id[listing_id] = score
        
        # Process description results
        for point in description_results:
            listing_id = point.id
            score = point.score
            if listing_id not in scores_by_id or score > scores_by_id[listing_id]:
                scores_by_id[listing_id] = score
        
        # Sort by score descending and take top limit
        sorted_results = sorted(
            scores_by_id.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return sorted_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise RuntimeError(f"Search failed: {e}") from e


def get_listings_by_ids(
    listing_ids: List[int],
    db: Session,
) -> List[Listing]:
    """
    Fetch listing objects from PostgreSQL by IDs.
    
    Args:
        listing_ids: List of listing IDs
        db: Database session
        
    Returns:
        List of Listing objects in the same order as listing_ids
    """
    if not listing_ids:
        return []
    
    listings = db.query(Listing).filter(Listing.id.in_(listing_ids)).all()
    
    # Sort to match the order of listing_ids
    listings_by_id = {listing.id: listing for listing in listings}
    return [listings_by_id[id] for id in listing_ids if id in listings_by_id]
