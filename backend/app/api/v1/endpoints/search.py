"""
Search API endpoint.
Handles semantic search requests.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.schemas.listing import ListingResponse
from app.services.search_service import search_listings, get_listings_by_ids

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., description="Search query in Hebrew", min_length=1),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of results"),
    price_min: Optional[int] = Query(default=None, ge=0, description="Minimum price"),
    price_max: Optional[int] = Query(default=None, ge=0, description="Maximum price"),
    rooms_min: Optional[float] = Query(default=None, ge=0, description="Minimum rooms"),
    rooms_max: Optional[float] = Query(default=None, ge=0, description="Maximum rooms"),
    city: Optional[str] = Query(default=None, description="Filter by city"),
    location: Optional[str] = Query(default=None, description="Filter by location"),
    has_parking: Optional[bool] = Query(default=None, description="Has parking"),
    has_elevator: Optional[bool] = Query(default=None, description="Has elevator"),
    furnished: Optional[bool] = Query(default=None, description="Furnished"),
    db: Session = Depends(get_db),
):
    """
    Semantic search endpoint.
    
    Performs semantic search on apartment listings using vector similarity.
    Uses multivector search (structured + description vectors) with MAX_SIM strategy.
    Supports filtering by structured fields (price, rooms, city, etc.).
    
    Args:
        query: Search query in Hebrew
        limit: Maximum number of results (1-100)
        price_min: Minimum price filter
        price_max: Maximum price filter
        rooms_min: Minimum rooms filter
        rooms_max: Maximum rooms filter
        city: City filter
        location: Location/neighborhood filter
        has_parking: Parking filter
        has_elevator: Elevator filter
        furnished: Furnished filter
        db: Database session
        
    Returns:
        SearchResponse with ranked results
    """
    try:
        # Build filter dictionary
        filters = {
            "price_min": price_min,
            "price_max": price_max,
            "rooms_min": rooms_min,
            "rooms_max": rooms_max,
            "city": city,
            "location": location,
            "has_parking": has_parking,
            "has_elevator": has_elevator,
            "furnished": furnished,
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Perform search
        search_results = search_listings(
            query=query,
            limit=limit,
            filters=filters if filters else None,
        )
        
        if not search_results:
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                limit=limit,
            )
        
        # Extract IDs and scores
        listing_ids = [listing_id for listing_id, _ in search_results]
        scores = {listing_id: score for listing_id, score in search_results}
        
        # Fetch full listing data from PostgreSQL
        listings = get_listings_by_ids(listing_ids, db)
        
        # Build response
        results = [
            SearchResult(
                listing=ListingResponse.model_validate(listing),
                score=scores[listing.id],
                rank=rank + 1,
            )
            for rank, listing in enumerate(listings)
        ]
        
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            limit=limit,
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
