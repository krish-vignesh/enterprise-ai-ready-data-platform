"""FastAPI dependencies for database session management."""

from collections.abc import Generator
#Generator is imported from collections.abc to provide type hinting for the get_db function, indicating that it yields a SQLAlchemy Session object.

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide one database session and close it after use."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()