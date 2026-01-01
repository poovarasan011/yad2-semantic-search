"""
Ingest API endpoint.
Manual trigger for ETL pipeline.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
import sys
from pathlib import Path

# Add project root and etl directory to path BEFORE importing etl
# Path from backend/app/api/v1/endpoints/ingest.py to project root: ../../../../../../
# backend/app/api/v1/endpoints/ -> backend/app/api/v1/ -> backend/app/api/ -> backend/app/ -> backend/ -> project_root
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
etl_dir = project_root / "etl"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(etl_dir) not in sys.path:
    sys.path.insert(0, str(etl_dir))

logger = logging.getLogger(__name__)

router = APIRouter()


def run_etl_pipeline():
    """Run the ETL pipeline."""
    try:
        # Import after adding project root to path
        from etl.main import ingest_listings_flow
        result = ingest_listings_flow()
        logger.info(f"ETL pipeline completed: {result}")
        return result
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}", exc_info=True)
        raise


@router.post("/ingest")
async def trigger_ingest(background_tasks: BackgroundTasks):
    """
    Trigger ETL pipeline to ingest listings.
    
    Runs the ETL pipeline as a background task.
    
    Returns:
        Success message
    """
    try:
        # Run ETL pipeline in background
        background_tasks.add_task(run_etl_pipeline)
        
        return {
            "status": "accepted",
            "message": "ETL pipeline started in background",
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger ETL pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger ETL: {str(e)}")
