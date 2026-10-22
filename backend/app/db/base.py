"""Central SQLAlchemy declarative base for the application models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared base class for all ORM models in the platform."""

    pass


__all__ = ["Base"]
