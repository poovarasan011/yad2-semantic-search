"""
Pydantic schemas for Listing model.
Request/response models for listings.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ListingBase(BaseModel):
    """Base listing schema with common fields."""
    external_id: str
    title: Optional[str] = None
    description: str
    price: Optional[int] = None
    rooms: Optional[float] = None
    size_sqm: Optional[int] = None
    location: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    has_parking: bool = False
    has_elevator: bool = False
    has_balcony: bool = False
    has_storage: bool = False
    furnished: bool = False
    pets_allowed: Optional[bool] = None


class ListingResponse(ListingBase):
    """Listing response schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    scraped_at: datetime
    
    model_config = {"from_attributes": True}


class ListingCreate(ListingBase):
    """Listing creation schema."""
    pass


class ListingUpdate(BaseModel):
    """Listing update schema (all fields optional)."""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    rooms: Optional[float] = None
    size_sqm: Optional[int] = None
    location: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    has_parking: Optional[bool] = None
    has_elevator: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_storage: Optional[bool] = None
    furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
