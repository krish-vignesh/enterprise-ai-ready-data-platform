
"""Orchestrate company registration and initial owner membership."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.company_membership import CompanyMembership, CompanyRole
from app.repositories.company_membership_repository import (
    CompanyMembershipRepository,
)
from app.repositories.company_repository import CompanyRepository


logger = logging.getLogger(__name__)


class CompanyRegistrationService:
    """Register a company and assign its initial owner atomically."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service using the caller-provided session."""
        self.session = session
        self.company_repository = CompanyRepository(session)
        self.membership_repository = CompanyMembershipRepository(session)

    async def register_company(
        self,
        *,
        company_name: str,
        user_id: UUID,
    ) -> Company:
        """Create a company and its initial OWNER membership."""

        try:
            async with self.session.begin():
                company = Company(company_name=company_name)

                self.company_repository.add(company)

                # Execute the INSERT to generate the company UUID.
                await self.session.flush()

                membership = CompanyMembership(
                    company_id=company.company_id,
                    user_id=user_id,
                    role=CompanyRole.OWNER,
                )

                self.membership_repository.add(membership)

                # Execute the membership INSERT before committing.
                await self.session.flush()

            logger.info(
                "company.registration.completed company_id=%s user_id=%s",
                company.company_id,
                user_id,
            )

            return company

        except Exception:
            logger.exception(
                "company.registration.failed user_id=%s",
                user_id,
            )
            raise
