"""Reusable SQLAlchemy model fields and mixins."""

from datetime import datetime, timezone


from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from uuid6 import uuid7


def uuid7_primary_key():
    """Create a UUIDv7 primary-key column for a model."""
    return mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )


class TimestampMixin:
    """Provide creation and update timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
