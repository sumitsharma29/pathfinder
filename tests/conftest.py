import pytest
import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.session import SessionLocal, engine
from backend.app.db.base import Base


@pytest.fixture(scope="session")
def db_session():
    """Provides a transactional database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
