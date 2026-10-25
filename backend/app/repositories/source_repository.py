"""Repository for SourceSystem persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source_system import SourceSystem


logger = logging.getLogger(__name__)


class SourceSystemRepository:
    """Provide database access for source-system records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
        self,
        source_id: UUID,
    ) -> SourceSystem | None:
        """Return a source system by UUID, or None if not found."""
        try:
            source = await self.session.get(SourceSystem, source_id)

            logger.debug(
                "repository.source_system.get_by_id completed source_id=%s found=%s",
                source_id,
                source is not None,
            )

            return source

        except Exception:
            logger.exception(
                "repository.source_system.get_by_id failed source_id=%s",
                source_id,
            )
            raise

    async def list_by_company(
        self,
        company_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[SourceSystem]:
        """Return a paginated list of source systems for a company."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(SourceSystem)
            .where(SourceSystem.company_id == company_id)
            .order_by(
                SourceSystem.created_at,
                SourceSystem.source_id,
            )
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            sources = list(result.all())

            logger.debug(
                "repository.source_system.list_by_company completed "
                "company_id=%s limit=%s offset=%s result_count=%s",
                company_id,
                limit,
                offset,
                len(sources),
            )

            return sources

        except Exception:
            logger.exception(
                "repository.source_system.list_by_company failed company_id=%s",
                company_id,
            )
            raise

    def add(self, source: SourceSystem) -> SourceSystem:
        """Stage a source system for persistence without committing."""
        try:
            self.session.add(source)

            logger.debug("repository.source_system.add staged")

            return source

        except Exception:
            logger.exception("repository.source_system.add failed")
            raise
