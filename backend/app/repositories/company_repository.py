"""Repository for Company persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


logger = logging.getLogger(__name__)


class CompanyRepository:
    """Provide database access for Company records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(self, company_id: UUID) -> Company | None:
        """Return a company by UUID, or None if it does not exist."""
        try:
            company = await self.session.get(Company, company_id)

            logger.debug(
                "repository.company.get_by_id completed company_id=%s found=%s",
                company_id,
                company is not None,
            )

            return company

        except Exception:
            logger.exception(
                "repository.company.get_by_id failed company_id=%s",
                company_id,
            )
            raise

    async def list_paginated(
        self,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[Company]:
        """Return companies in deterministic order with pagination."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(Company)
            .order_by(Company.created_at, Company.company_id)
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            companies = list(result.all())

            logger.debug(
                "repository.company.list_paginated completed "
                "limit=%s offset=%s result_count=%s",
                limit,
                offset,
                len(companies),
            )

            return companies

        except Exception:
            logger.exception(
                "repository.company.list_paginated failed limit=%s offset=%s",
                limit,
                offset,
            )
            raise

    def add(self, company: Company) -> Company:
        """Stage a company for persistence without committing."""
        try:
            self.session.add(company)

            logger.debug("repository.company.add staged")

            return company

        except Exception:
            logger.exception("repository.company.add failed")
            raise
