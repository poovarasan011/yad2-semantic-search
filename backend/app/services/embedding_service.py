"""
Embedding Service for text-to-vector conversion.
Uses sentence-transformers models for semantic embeddings.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.db.models import Listing
from app.utils.structured_text import build_structured_text

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Singleton service for generating text embeddings.
    
    Loads the model once and reuses it for all encoding operations.
    Supports both single text and batch encoding.
    """
    
    _instance: Optional['EmbeddingService'] = None
    _model: Optional[SentenceTransformer] = None
    
    def __new__(cls):
        """Singleton pattern: ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding service."""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.device = settings.EMBEDDING_DEVICE
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self._model = None
        self._vector_size: Optional[int] = None
        self._initialized = True
        
        logger.info(
            f"EmbeddingService initialized: "
            f"model={self.model_name}, device={self.device}"
        )
    
    def _load_model(self) -> None:
        """
        Load the sentence transformer model.
        Called lazily on first use.
        """
        if self._model is not None:
            return
        
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
            
            # Cache vector size
            self._vector_size = self._model.get_sentence_embedding_dimension()
            
            logger.info(
                f"Model loaded successfully. "
                f"Vector dimension: {self._vector_size}, Device: {self.device}"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def get_model(self) -> SentenceTransformer:
        """
        Get the model instance, loading it if necessary.
        
        Returns:
            SentenceTransformer: The loaded model instance
            
        Raises:
            RuntimeError: If model loading fails
        """
        if self._model is None:
            self._load_model()
        return self._model
    
    def encode(self, text: str, normalize_embeddings: bool = True) -> np.ndarray:
        """
        Encode a single text string into a vector embedding.
        
        Args:
            text: The text to encode
            normalize_embeddings: Whether to normalize embeddings to unit length
            
        Returns:
            numpy.ndarray: Vector embedding (shape: (vector_size,))
            
        Raises:
            ValueError: If text is empty
            RuntimeError: If encoding fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            model = self.get_model()
            embedding = model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=normalize_embeddings,
                show_progress_bar=False,
            )
            
            # Model.encode returns 2D array for single text, get first row
            if embedding.ndim == 2:
                embedding = embedding[0]
            
            return embedding
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise RuntimeError(f"Encoding failed: {e}") from e
    
    def encode_batch(
        self,
        texts: List[str],
        normalize_embeddings: bool = True,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Encode multiple texts into vector embeddings efficiently.
        
        Args:
            texts: List of texts to encode
            normalize_embeddings: Whether to normalize embeddings to unit length
            show_progress: Whether to show progress bar (useful for large batches)
            
        Returns:
            numpy.ndarray: Array of embeddings (shape: (len(texts), vector_size))
            
        Raises:
            ValueError: If texts list is empty
            RuntimeError: If encoding fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        try:
            model = self.get_model()
            embeddings = model.encode(
                texts,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=normalize_embeddings,
                show_progress_bar=show_progress,
            )
            
            return embeddings
        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            raise RuntimeError(f"Batch encoding failed: {e}") from e
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information including name, device, vector size
        """
        model = self.get_model()
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "vector_size": self._vector_size or model.get_sentence_embedding_dimension(),
            "batch_size": self.batch_size,
            "is_loaded": self._model is not None,
        }
    
    def get_vector_size(self) -> int:
        """
        Get the dimension of vectors produced by this model.
        
        Returns:
            int: Vector dimension (e.g., 768 for multilingual-e5-base)
        """
        if self._vector_size is None:
            model = self.get_model()
            self._vector_size = model.get_sentence_embedding_dimension()
        return self._vector_size
    
    def encode_listing(self, listing: Listing) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encode a listing as multivector (structured + description).
        
        Generates two vectors:
        1. Structured vector: from extracted structured fields
        2. Description vector: from raw description text
        
        Args:
            listing: Listing model instance
            
        Returns:
            Tuple of (structured_vector, description_vector)
            Each vector is numpy array with shape (vector_size,)
            
        Raises:
            ValueError: If listing description is empty
            RuntimeError: If encoding fails
        """
        # Generate structured text
        structured_text = build_structured_text(listing)
        
        # Encode structured text
        structured_vector = self.encode(structured_text)
        
        # Encode description
        if not listing.description or not listing.description.strip():
            raise ValueError("Listing description cannot be empty")
        description_vector = self.encode(listing.description)
        
        return structured_vector, description_vector
    
    def encode_listings_batch(
        self, 
        listings: List[Listing],
        show_progress: bool = False,
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Encode multiple listings efficiently using batch processing.
        
        Processes structured texts and descriptions in separate batches
        for optimal performance.
        
        Args:
            listings: List of Listing model instances
            show_progress: Whether to show progress bar
            
        Returns:
            List of tuples: [(structured_vec, desc_vec), ...]
            
        Raises:
            ValueError: If listings list is empty
            RuntimeError: If encoding fails
        """
        if not listings:
            raise ValueError("Listings list cannot be empty")
        
        # Build structured texts
        structured_texts = [build_structured_text(listing) for listing in listings]
        descriptions = [listing.description for listing in listings]
        
        # Batch encode structured texts
        structured_vectors = self.encode_batch(
            structured_texts,
            show_progress=show_progress,
        )
        
        # Batch encode descriptions
        description_vectors = self.encode_batch(
            descriptions,
            show_progress=show_progress,
        )
        
        # Pair them up
        result = [
            (structured_vectors[i], description_vectors[i])
            for i in range(len(listings))
        ]
        
        return result


# Global singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the global EmbeddingService instance.
    
    Returns:
        EmbeddingService: The singleton service instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
