"""
Pytest configuration and shared fixtures for testing.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so we can import app modules
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.db.qdrant import QdrantManager
from app.core.config import Settings


@pytest.fixture(scope="function")
def test_settings():
    """Create test settings with in-memory database."""
    return Settings(
        POSTGRES_DB="test_db",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_pass",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        QDRANT_HOST="localhost",
        QDRANT_PORT=6333,
        QDRANT_COLLECTION_NAME="test_apartments",
        DEBUG=True,
    )


@pytest.fixture(scope="function")
def test_db_session(test_settings):
    """
    Create a test database session with in-memory SQLite for unit tests.
    Note: For integration tests, use actual PostgreSQL.
    """
    # Use SQLite in-memory for unit tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def qdrant_manager_mock(test_settings):
    """Mock Qdrant manager for testing."""
    manager = QdrantManager()
    manager.collection_name = test_settings.QDRANT_COLLECTION_NAME
    manager.vector_size = test_settings.QDRANT_VECTOR_SIZE
    return manager

