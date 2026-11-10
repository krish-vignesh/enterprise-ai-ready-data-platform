"""add users and company memberships

Revision ID: 4be6457302de
Revises: 4bcaba23a6ad
Create Date: 2026-11-10 14:59:09.971268

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4be6457302de"
down_revision: Union[str, Sequence[str], None] = "4bcaba23a6ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Create users first.
    op.create_table(
        "users",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("keycloak_subject", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint(
            "keycloak_subject",
            name="uq_users_keycloak_subject",
        ),
    )

    # 2. Create company_memberships after users.
    op.create_table(
        "company_memberships",
        sa.Column("membership_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "OWNER",
                "ADMIN",
                "MEMBER",
                name="company_role",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.company_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("membership_id"),
        sa.UniqueConstraint(
            "user_id",
            "company_id",
            name="uq_company_memberships_user_company",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop dependent table first.
    op.drop_table("company_memberships")

    # Then drop its referenced users table.
    op.drop_table("users")
