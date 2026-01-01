"""
PostgreSQL loader for batch inserting listings.
Handles bulk inserts with proper error handling and deduplication.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.models import Listing
from app.db.session import get_db_session


def load_listings_to_postgres(
    listings: List[Dict[str, Any]],
    session: Optional[Session] = None,
    batch_size: int = 100,
) -> Dict[str, int]:
    """
    Load listings into PostgreSQL database.
    
    Uses upsert (INSERT ... ON CONFLICT) to handle duplicates based on external_id.
    
    Args:
        listings: List of listing dictionaries
        session: Optional database session (creates new if not provided)
        batch_size: Number of records to insert per batch
        
    Returns:
        Dictionary with counts: {"inserted": int, "updated": int, "errors": int}
    """
    if not listings:
        return {"inserted": 0, "updated": 0, "errors": 0}
    
    use_external_session = session is not None
    if not use_external_session:
        session = get_db_session()
    
    inserted_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        # Process in batches
        for i in range(0, len(listings), batch_size):
            batch = listings[i:i + batch_size]
            
            try:
                # Prepare data for upsert
                values = []
                for listing in batch:
                    value_dict = {
                        "external_id": listing.get("external_id"),
                        "title": listing.get("title"),
                        "description": listing.get("description"),
                        "price": listing.get("price"),
                        "rooms": listing.get("rooms"),
                        "size_sqm": listing.get("size_sqm"),
                        "location": listing.get("location"),
                        "city": listing.get("city"),
                        "neighborhood": listing.get("neighborhood"),
                        "floor": listing.get("floor"),
                        "total_floors": listing.get("total_floors"),
                        "has_parking": listing.get("has_parking", False),
                        "has_elevator": listing.get("has_elevator", False),
                        "has_balcony": listing.get("has_balcony", False),
                        "has_storage": listing.get("has_storage", False),
                        "furnished": listing.get("furnished", False),
                        "pets_allowed": listing.get("pets_allowed"),
                        "scraped_at": datetime.now(),
                    }
                    
                    # Only add if external_id exists (required field)
                    if value_dict["external_id"]:
                        values.append(value_dict)
                
                if not values:
                    continue
                
                # Upsert using PostgreSQL ON CONFLICT
                stmt = insert(Listing.__table__).values(values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["external_id"],
                    set_=dict(
                        title=stmt.excluded.title,
                        description=stmt.excluded.description,
                        price=stmt.excluded.price,
                        rooms=stmt.excluded.rooms,
                        size_sqm=stmt.excluded.size_sqm,
                        location=stmt.excluded.location,
                        city=stmt.excluded.city,
                        neighborhood=stmt.excluded.neighborhood,
                        floor=stmt.excluded.floor,
                        total_floors=stmt.excluded.total_floors,
                        has_parking=stmt.excluded.has_parking,
                        has_elevator=stmt.excluded.has_elevator,
                        has_balcony=stmt.excluded.has_balcony,
                        has_storage=stmt.excluded.has_storage,
                        furnished=stmt.excluded.furnished,
                        pets_allowed=stmt.excluded.pets_allowed,
                        scraped_at=stmt.excluded.scraped_at,
                    )
                )
                
                result = session.execute(stmt)
                session.commit()
                
                # Fetch the inserted/updated listing IDs
                # We need these for Qdrant point IDs
                external_ids = [v["external_id"] for v in values]
                listings_with_ids = session.query(Listing).filter(
                    Listing.external_id.in_(external_ids)
                ).all()
                
                # Add IDs to the original listings
                for listing_obj in listings_with_ids:
                    # Find corresponding listing in batch and add id
                    for listing in batch:
                        if listing.get("external_id") == listing_obj.external_id:
                            listing["id"] = listing_obj.id
                            break
                
                # Note: PostgreSQL doesn't return detailed counts for upsert
                # We'll approximate: if external_id exists, it's an update; otherwise insert
                # For simplicity, we'll count all as "inserted" (upsert handles both)
                inserted_count += len(values)
                
            except Exception as e:
                error_count += len(batch)
                session.rollback()
                print(f"Error loading batch {i//batch_size + 1}: {e}")
                continue
        
        if not use_external_session:
            session.close()
        
        return {
            "inserted": inserted_count,
            "updated": updated_count,  # Approximate - upsert handles both
            "errors": error_count,
        }
        
    except Exception as e:
        if not use_external_session:
            session.close()
        raise RuntimeError(f"Failed to load listings to PostgreSQL: {e}") from e
