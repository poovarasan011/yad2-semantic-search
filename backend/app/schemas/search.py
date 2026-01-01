"""
Pydantic schemas for search requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.listing import ListingResponse


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., description="Search query in Hebrew", min_length=1)
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    
    # Structured filters
    price_min: Optional[int] = Field(default=None, ge=0, description="Minimum price in NIS")
    price_max: Optional[int] = Field(default=None, ge=0, description="Maximum price in NIS")
    rooms_min: Optional[float] = Field(default=None, ge=0, description="Minimum number of rooms")
    rooms_max: Optional[float] = Field(default=None, ge=0, description="Maximum number of rooms")
    city: Optional[str] = Field(default=None, description="Filter by city")
    location: Optional[str] = Field(default=None, description="Filter by location/neighborhood")
    has_parking: Optional[bool] = Field(default=None, description="Filter by parking availability")
    has_elevator: Optional[bool] = Field(default=None, description="Filter by elevator availability")
    furnished: Optional[bool] = Field(default=None, description="Filter by furnished status")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "דירה 2 חדרים בתל אביב",
                "limit": 10,
                "price_max": 8000,
                "city": "תל אביב",
            }
        }
    }


class SearchResult(BaseModel):
    """Individual search result with similarity score."""
    listing: ListingResponse
    score: float = Field(..., description="Similarity score (0-1)")
    rank: int = Field(..., description="Result rank (1-based)")


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[SearchResult]
    total_results: int
    limit: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "דירה 2 חדרים בתל אביב",
                "results": [],
                "total_results": 0,
                "limit": 10,
            }
        }
    }
