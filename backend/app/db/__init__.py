"""Database package for the application.

This package centralizes the SQLAlchemy declarative base and the engine/session
lifecycle used by the platform.
"""

from app.db.base import Base
from app.db.session import SessionLocal, engine

__all__ = ["Base", "SessionLocal", "engine"]
