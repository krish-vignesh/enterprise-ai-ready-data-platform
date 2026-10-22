
"""Document entity for the platform catalog."""

from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import DocumentStatus
from app.models.mixins import TimestampMixin, uuid7_primary_key


class Document(TimestampMixin, Base):
    """Represent an uploaded file registered in a dataset."""

    __tablename__ = "documents"

    __table_args__ = (
        UniqueConstraint(
            "dataset_id",
            "sha256",
            name="uq_documents_dataset_id_sha256",
        ),
        CheckConstraint(
            "file_size_bytes >= 0",
            name="ck_documents_file_size_nonnegative",
        ),
        CheckConstraint(
            "status IN ('UPLOADING', 'AVAILABLE', 'FAILED', 'RECONCILIATION_REQUIRED')",
            name="ck_documents_status_valid",
        ),
    )

    document_id = uuid7_primary_key()

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasets.dataset_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    detected_format: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SQLAlchemyEnum(
            DocumentStatus,
            name="document_status",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
        ),
        nullable=False,
        default=DocumentStatus.UPLOADING,
    )
