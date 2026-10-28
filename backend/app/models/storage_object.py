"""Storage object entity for the platform catalog."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid7_primary_key


class StorageObject(TimestampMixin, Base):
    """Represent a document's physical storage location."""

    __tablename__ = "storage_objects"

    __table_args__ = (
        UniqueConstraint(
            "bucket_name",
            "object_key",
            name="uq_storage_objects_bucket_name_object_key",
        ),
    )

    storage_object_id = uuid7_primary_key()

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.document_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    bucket_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    object_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
