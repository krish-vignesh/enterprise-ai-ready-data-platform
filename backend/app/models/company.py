
"""Company entity for the platform catalog."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid7_primary_key


class Company(TimestampMixin, Base):
    """Represent a company registered in the platform."""

    __tablename__ = "companies"

    company_id = uuid7_primary_key()

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
