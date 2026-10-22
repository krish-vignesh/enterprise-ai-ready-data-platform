
"""Dataset entity for the platform catalog."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid7_primary_key


class Dataset(TimestampMixin, Base):
    """Represent a dataset provided by a source system."""

    __tablename__ = "datasets"

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "dataset_name",
            name="uq_datasets_source_id_dataset_name",
        ),
    )

    dataset_id = uuid7_primary_key()

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_systems.source_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
