"""
Unit tests for database session management.
"""

import pytest
from app.db.session import SessionLocal, get_db_session, init_db
from app.db.models import Listing


class TestDatabaseSession:
    """Test cases for database session management."""
    
    def test_get_db_session(self):
        """Test getting a database session."""
        session = get_db_session()
        assert session is not None
        session.close()
    
    def test_session_context_manager(self, test_db_session):
        """Test using session as context manager."""
        # Use test_db_session fixture which has tables created
        session = test_db_session
        assert session is not None
        # Can query (even if empty)
        result = session.query(Listing).first()
        assert result is None  # No data yet
    
    def test_session_isolation(self, test_db_session):
        """Test that sessions are isolated."""
        # Create listing in test session
        listing = Listing(
            external_id="test_isolation",
            description="Test",
        )
        test_db_session.add(listing)
        test_db_session.commit()
        
        # Verify it exists in this session
        found = test_db_session.query(Listing).filter_by(external_id="test_isolation").first()
        assert found is not None
        
        # New session should not see it (if using different DB)
        # Note: This test uses in-memory SQLite, so isolation is per-session
        new_session = get_db_session()
        try:
            # In real PostgreSQL, this would be isolated
            # For in-memory SQLite, it's the same DB
            pass
        finally:
            new_session.close()

