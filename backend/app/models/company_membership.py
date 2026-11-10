"""Company membership entity for company-level user authorization."""

from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid7_primary_key


class CompanyRole(str, Enum):
    """Roles a user can hold within a company."""

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class CompanyMembership(TimestampMixin, Base):
    """Associate a platform user with a company and their assigned role."""

    __tablename__ = "company_memberships"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "company_id",
            name="uq_company_memberships_user_company",
        ),
    )

    membership_id = uuid7_primary_key()

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.company_id"),
        nullable=False,
    )

    role: Mapped[CompanyRole] = mapped_column(
        SQLAlchemyEnum(
            CompanyRole,
            name="company_role",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
