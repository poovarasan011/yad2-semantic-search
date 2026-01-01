"""
SQLAlchemy models for PostgreSQL database.
Defines the Listing model matching the database schema.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Listing(Base):
    """
    Listing model representing an apartment listing from Yad2 or other sources.
    This is the ground truth data stored in PostgreSQL.
    """
    
    __tablename__ = "listings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # External identifier (from Yad2 or other source)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Basic information
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=False)  # Full Hebrew description
    
    # Pricing and size
    price = Column(Integer, nullable=True, index=True)  # Price in NIS
    rooms = Column(Numeric(3, 1), nullable=True, index=True)  # e.g., 2.5, 3, 4.5
    size_sqm = Column(Integer, nullable=True)  # Square meters
    
    # Location
    location = Column(Text, nullable=True, index=True)  # Neighborhood/area
    city = Column(String(100), nullable=True, index=True)
    neighborhood = Column(String(100), nullable=True)
    
    # Building details
    floor = Column(Integer, nullable=True)
    total_floors = Column(Integer, nullable=True)
    
    # Features (boolean flags)
    has_parking = Column(Boolean, default=False, nullable=False)
    has_elevator = Column(Boolean, default=False, nullable=False)
    has_balcony = Column(Boolean, default=False, nullable=False)
    has_storage = Column(Boolean, default=False, nullable=False)
    furnished = Column(Boolean, default=False, nullable=False)  # מרוהט
    pets_allowed = Column(Boolean, nullable=True)  # NULL = not specified
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<Listing(id={self.id}, external_id='{self.external_id}', city='{self.city}', rooms={self.rooms}, price={self.price})>"
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "rooms": float(self.rooms) if self.rooms else None,
            "size_sqm": self.size_sqm,
            "location": self.location,
            "city": self.city,
            "neighborhood": self.neighborhood,
            "floor": self.floor,
            "total_floors": self.total_floors,
            "has_parking": self.has_parking,
            "has_elevator": self.has_elevator,
            "has_balcony": self.has_balcony,
            "has_storage": self.has_storage,
            "furnished": self.furnished,
            "pets_allowed": self.pets_allowed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }
