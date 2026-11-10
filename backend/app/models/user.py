"""User entity for platform identity mapping."""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid7_primary_key


class User(TimestampMixin, Base):
    """Map an external Keycloak identity to an internal platform user."""

    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint(
            "keycloak_subject",
            name="uq_users_keycloak_subject",
        ),
    )

    user_id = uuid7_primary_key()

    keycloak_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
