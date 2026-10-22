
"""Upload attempt entity for the platform catalog."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import UploadAttemptStatus
from app.models.mixins import TimestampMixin, uuid7_primary_key


class UploadAttempt(TimestampMixin, Base):
    """Record one attempt to upload a document."""

    __tablename__ = "upload_attempts"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "attempt_number",
            name="uq_upload_attempts_document_id_attempt_number",
        ),
        CheckConstraint(
            "attempt_number > 0",
            name="ck_upload_attempts_attempt_number_positive",
        ),
        CheckConstraint(
            "status IN ('IN_PROGRESS', 'SUCCEEDED', 'FAILED')",
            name="ck_upload_attempts_status_valid",
        ),
    )

    upload_attempt_id = uuid7_primary_key()

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.document_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[UploadAttemptStatus] = mapped_column(
        SQLAlchemyEnum(
            UploadAttemptStatus,
            name="upload_attempt_status",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
        ),
        nullable=False,
        default=UploadAttemptStatus.IN_PROGRESS,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failure_code: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    failure_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    request_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
