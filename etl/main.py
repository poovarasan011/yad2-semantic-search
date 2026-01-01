"""
ETL Pipeline Entry Point
Main Prefect flow for ingesting listings data.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from prefect import flow, task
from datetime import datetime
from dotenv import load_dotenv


# Add project root and backend to path for imports
# In Docker, the project root is mounted at /workspace
# In local development, it's 1 level up from etl/main.py
if Path("/workspace").exists():
    # Docker environment
    project_root = Path("/workspace")
    backend_dir = project_root / "backend"
else:
    # Local development
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load .env file
if Path("/workspace/.env").exists():
    # Docker environment
    load_dotenv(dotenv_path="/workspace/.env")
else:
    # Local development
    load_dotenv(dotenv_path=project_root / ".env")

# Use relative imports when etl is imported as a module, absolute when run as script
# Add etl directory to path to support absolute imports
etl_dir = Path(__file__).parent
if str(etl_dir) not in sys.path:
    sys.path.insert(0, str(etl_dir))

from scrapers.mock_scraper import get_mock_listings
from processors.cleaner import clean_listings
from processors.vectorizer import generate_listings_embeddings_batch
from loaders.postgres_loader import load_listings_to_postgres
from loaders.qdrant_loader import load_vectors_to_qdrant
from app.core.config import settings
from app.db.session import init_db
from app.db.qdrant import init_qdrant


@task(name="scrape_listings")
def scrape_listings_task() -> List[Dict[str, Any]]:
    """
    Scrape listings from data source.
    
    Currently uses mock scraper. In Phase 2, this will use real Yad2 scraper.
    
    Returns:
        List of raw listing dictionaries
    """
    print("📥 Scraping listings...")
    listings = get_mock_listings()
    print(f"✓ Scraped {len(listings)} listings")
    return listings


@task(name="clean_listings")
def clean_listings_task(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean and normalize listing data.
    
    Args:
        listings: Raw listing dictionaries
        
    Returns:
        Cleaned listing dictionaries
    """
    print("🧹 Cleaning listings...")
    cleaned = clean_listings(listings)
    print(f"✓ Cleaned {len(cleaned)} listings")
    return cleaned


@task(name="generate_embeddings")
def generate_embeddings_task(listings: List[Dict[str, Any]]) -> tuple:
    """
    Generate embeddings for listings.
    
    Args:
        listings: Cleaned listing dictionaries
        
    Returns:
        Tuple of (listings, embeddings) where embeddings is list of (structured_vec, desc_vec)
    """
    print("🔢 Generating embeddings...")
    embeddings = generate_listings_embeddings_batch(listings, show_progress=True)
    print(f"✓ Generated embeddings for {len(embeddings)} listings")
    return listings, embeddings


@task(name="load_to_postgres")
def load_to_postgres_task(listings: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Load listings to PostgreSQL.
    
    Args:
        listings: Cleaned listing dictionaries
        
    Returns:
        Dictionary with load statistics
    """
    print("💾 Loading to PostgreSQL...")
    results = load_listings_to_postgres(listings)
    print(f"✓ Loaded to PostgreSQL: {results}")
    return results


@task(name="load_to_qdrant")
def load_to_qdrant_task(
    listings: List[Dict[str, Any]],
    embeddings: List,
) -> Dict[str, int]:
    """
    Load vectors to Qdrant.
    
    Args:
        listings: Cleaned listing dictionaries
        embeddings: List of (structured_vec, desc_vec) tuples
        
    Returns:
        Dictionary with load statistics
    """
    print("🔍 Loading vectors to Qdrant...")
    results = load_vectors_to_qdrant(
        listings,
        embeddings,
        collection_name=settings.QDRANT_COLLECTION_NAME,
    )
    print(f"✓ Loaded to Qdrant: {results}")
    return results


@flow(name="ingest_listings", log_prints=True)
def ingest_listings_flow():
    """
    Main ETL flow for ingesting apartment listings.
    
    Flow:
    1. Initialize databases (PostgreSQL schema, Qdrant collection)
    2. Scrape listings (mock for now)
    3. Clean and normalize data
    4. Generate embeddings (structured + description vectors)
    5. Load to PostgreSQL (structured data)
    6. Load to Qdrant (vectors)
    """
    print("=" * 80)
    print("ETL PIPELINE: Ingest Listings")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}\n")
    
    try:
        # Initialize databases
        print("🔧 Initializing databases...")
        init_db()
        init_qdrant()
        print("✓ Databases initialized\n")
        
        # Step 1: Scrape
        raw_listings = scrape_listings_task()
        
        # Step 2: Clean
        cleaned_listings = clean_listings_task(raw_listings)
        
        # Step 3: Generate embeddings
        listings, embeddings = generate_embeddings_task(cleaned_listings)
        
        # Step 4: Load to PostgreSQL
        postgres_results = load_to_postgres_task(listings)
        
        # Step 5: Load to Qdrant
        qdrant_results = load_to_qdrant_task(listings, embeddings)
        
        print("\n" + "=" * 80)
        print("ETL PIPELINE COMPLETE")
        print("=" * 80)
        print(f"PostgreSQL: {postgres_results}")
        print(f"Qdrant: {qdrant_results}")
        print(f"Completed at: {datetime.now().isoformat()}")
        
        return {
            "postgres": postgres_results,
            "qdrant": qdrant_results,
            "total_listings": len(listings),
        }
        
    except Exception as e:
        print(f"\n❌ ETL Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Run the flow
    result = ingest_listings_flow()
    print(f"\nResult: {result}")
