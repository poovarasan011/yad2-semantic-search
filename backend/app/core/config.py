"""
Configuration and settings management using Pydantic Settings.
Loads configuration from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Yad2 Semantic Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "yad2_search"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL database URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Qdrant Vector Database
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "apartments"
    QDRANT_VECTOR_SIZE: int = 768  # For multilingual-e5-base (768 dims)
    
    @property
    def QDRANT_URL(self) -> str:
        """Construct Qdrant URL."""
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
    
    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "intfloat/multilingual-e5-base"
    EMBEDDING_DEVICE: str = "cpu"  # "cpu" or "cuda"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:8501"]  # Streamlit default port
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )


# Global settings instance
settings = Settings()
