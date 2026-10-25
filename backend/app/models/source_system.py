
"""Source system entity for the platform catalog."""

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid7_primary_key


class SourceSystem(TimestampMixin, Base):
    """Represent a data source belonging to a company."""

    __tablename__ = "source_systems"

    source_id = uuid7_primary_key()

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.company_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
