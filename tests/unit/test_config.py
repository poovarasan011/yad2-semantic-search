"""
Unit tests for configuration management.
"""

import pytest
from app.core.config import Settings


class TestSettings:
    """Test cases for Settings configuration."""
    
    def test_default_settings(self):
        """Test that default settings are loaded."""
        # Create settings with explicit values to override any env vars
        # This ensures the test is not affected by environment variables
        settings = Settings(
            POSTGRES_USER="postgres",
            POSTGRES_PASSWORD="postgres",
            POSTGRES_HOST="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_DB="yad2_search",
            QDRANT_HOST="localhost",
            QDRANT_PORT=6333,
        )
        
        assert settings.APP_NAME == "Yad2 Semantic Search API"
        assert settings.POSTGRES_USER == "postgres"
        assert settings.QDRANT_COLLECTION_NAME == "apartments"
        assert settings.EMBEDDING_MODEL_NAME == "intfloat/multilingual-e5-base"
    
    def test_database_url_construction(self):
        """Test DATABASE_URL property construction."""
        settings = Settings(
            POSTGRES_USER="test_user",
            POSTGRES_PASSWORD="test_pass",
            POSTGRES_HOST="test_host",
            POSTGRES_PORT=5433,
            POSTGRES_DB="test_db",
        )
        
        url = settings.DATABASE_URL
        assert "test_user" in url
        assert "test_pass" in url
        assert "test_host" in url
        assert "5433" in url
        assert "test_db" in url
        assert url.startswith("postgresql://")
    
    def test_qdrant_url_construction(self):
        """Test QDRANT_URL property construction."""
        settings = Settings(
            QDRANT_HOST="qdrant_host",
            QDRANT_PORT=8080,
        )
        
        url = settings.QDRANT_URL
        assert "qdrant_host" in url
        assert "8080" in url
        assert url.startswith("http://")
    
    def test_custom_settings(self):
        """Test loading custom settings."""
        settings = Settings(
            DEBUG=True,
            LOG_LEVEL="DEBUG",
            POSTGRES_DB="custom_db",
        )
        
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.POSTGRES_DB == "custom_db"

