"""Repository for company membership persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_membership import CompanyMembership, CompanyRole


logger = logging.getLogger(__name__)


class CompanyMembershipRepository:
    """Provide database access for company membership records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
        self,
        membership_id: UUID,
    ) -> CompanyMembership | None:
        """Return a membership by internal UUID, or None if not found."""
        try:
            membership = await self.session.get(
                CompanyMembership,
                membership_id,
            )

            logger.debug(
                "repository.company_membership.get_by_id completed "
                "membership_id=%s found=%s",
                membership_id,
                membership is not None,
            )

            return membership

        except Exception:
            logger.exception(
                "repository.company_membership.get_by_id failed membership_id=%s",
                membership_id,
            )
            raise

    async def get_by_user_and_company(
        self,
        user_id: UUID,
        company_id: UUID,
    ) -> CompanyMembership | None:
        """Return a user's membership in a specific company."""
        statement = select(CompanyMembership).where(
            CompanyMembership.user_id == user_id,
            CompanyMembership.company_id == company_id,
        )

        try:
            result = await self.session.scalars(statement)
            membership = result.one_or_none()

            logger.debug(
                "repository.company_membership.get_by_user_and_company "
                "completed found=%s",
                membership is not None,
            )

            return membership

        except Exception:
            logger.exception(
                "repository.company_membership.get_by_user_and_company "
                "failed user_id=%s company_id=%s",
                user_id,
                company_id,
            )
            raise

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[CompanyMembership]:
        """Return all company memberships belonging to a user."""
        statement = select(CompanyMembership).where(
            CompanyMembership.user_id == user_id,
        )

        try:
            result = await self.session.scalars(statement)
            memberships = list(result.all())

            logger.debug(
                "repository.company_membership.get_by_user_id completed "
                "user_id=%s count=%s",
                user_id,
                len(memberships),
            )

            return memberships

        except Exception:
            logger.exception(
                "repository.company_membership.get_by_user_id failed user_id=%s",
                user_id,
            )
            raise

    async def get_by_company_id(
        self,
        company_id: UUID,
    ) -> list[CompanyMembership]:
        """Return all memberships belonging to a company."""
        statement = select(CompanyMembership).where(
            CompanyMembership.company_id == company_id,
        )

        try:
            result = await self.session.scalars(statement)
            memberships = list(result.all())

            logger.debug(
                "repository.company_membership.get_by_company_id completed "
                "company_id=%s count=%s",
                company_id,
                len(memberships),
            )

            return memberships

        except Exception:
            logger.exception(
                "repository.company_membership.get_by_company_id failed company_id=%s",
                company_id,
            )
            raise

    def add(
        self,
        membership: CompanyMembership,
    ) -> CompanyMembership:
        """Stage a membership for persistence without committing."""
        try:
            self.session.add(membership)

            logger.debug("repository.company_membership.add staged")

            return membership

        except Exception:
            logger.exception("repository.company_membership.add failed")
            raise

    def update_role(
        self,
        membership: CompanyMembership,
        *,
        role: CompanyRole,
    ) -> CompanyMembership:
        """Update the role assigned to a company membership."""
        try:
            membership.role = role

            logger.debug(
                "repository.company_membership.update_role staged membership_id=%s",
                membership.membership_id,
            )

            return membership

        except Exception:
            logger.exception(
                "repository.company_membership.update_role failed membership_id=%s",
                membership.membership_id,
            )
            raise

    async def delete(
        self,
        membership: CompanyMembership,
    ) -> None:
        """Stage a membership for deletion without committing."""
        try:
            await self.session.delete(membership)

            logger.debug(
                "repository.company_membership.delete staged membership_id=%s",
                membership.membership_id,
            )

        except Exception:
            logger.exception(
                "repository.company_membership.delete failed membership_id=%s",
                membership.membership_id,
            )
            raise
