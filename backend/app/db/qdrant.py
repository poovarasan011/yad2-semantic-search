"""
Qdrant vector database client setup and collection management.
Handles connection to Qdrant and collection initialization.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    CollectionStatus,
    PointStruct,
    Filter,
    FieldCondition,
    Range,
)
from qdrant_client.http import models
from typing import Optional, List, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantManager:
    """
    Manager for Qdrant vector database operations.
    Handles client connection and collection setup.
    """
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client: Optional[QdrantClient] = None
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.QDRANT_VECTOR_SIZE
        
    def connect(self) -> QdrantClient:
        """
        Create and return Qdrant client connection.
        Reuses existing connection if available.
        """
        if self.client is None:
            try:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    timeout=30,
                )
                logger.info(f"Connected to Qdrant at {settings.QDRANT_URL}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise
        return self.client
    
    def ensure_collection_exists(self) -> None:
        """
        Ensure the collection exists, create it if it doesn't.
        This should be called on application startup.
        """
        client = self.connect()
        
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            logger.info(f"Creating Qdrant collection: {self.collection_name} with named vectors (structured + description)")
            # Use named vectors approach for storing both structured and description vectors
            # This allows querying each vector separately or combining them in search
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "structured": VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                    "description": VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                },
            )
            logger.info(f"Collection '{self.collection_name}' created successfully with named vectors (structured + description)")
        else:
            logger.info(f"Collection '{self.collection_name}' already exists")
            
        # Verify collection status
        collection_info = client.get_collection(self.collection_name)
        if collection_info.status != CollectionStatus.GREEN:
            logger.warning(
                f"Collection '{self.collection_name}' status is {collection_info.status}"
            )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        client = self.connect()
        info = client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vector_size": info.config.params.vectors.size,
            "points_count": info.points_count,
            "status": info.status.value,
        }
    
    def health_check(self) -> bool:
        """
        Check if Qdrant is healthy and accessible.
        Returns True if healthy, False otherwise.
        """
        try:
            client = self.connect()
            collections = client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global Qdrant manager instance
qdrant_manager = QdrantManager()


def init_qdrant() -> None:
    """
    Initialize Qdrant connection and ensure collection exists.
    Should be called on application startup.
    """
    qdrant_manager.connect()
    qdrant_manager.ensure_collection_exists()


def get_qdrant_client() -> QdrantClient:
    """
    Get Qdrant client instance.
    Ensures connection is established.
    """
    return qdrant_manager.connect()
