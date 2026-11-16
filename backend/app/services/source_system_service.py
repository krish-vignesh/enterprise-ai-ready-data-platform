"""Service layer for source-system catalog operations."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source_system import SourceSystem
from app.repositories.source_repository import SourceSystemRepository


logger = logging.getLogger(__name__)


class SourceSystemService:
    """Orchestrate source-system creation and retrieval operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a request-scoped database session."""

        self.session = session
        self.source_repository = SourceSystemRepository(session)

    async def create_source_system(
        self,
        *,
        company_id: UUID,
        source_name: str,
        source_type: str,
    ) -> SourceSystem:
        """Create a source system for a company."""

        try:
            source = SourceSystem(
                company_id=company_id,
                source_name=source_name,
                source_type=source_type,
            )

            self.source_repository.add(source)

            await self.session.flush()
            await self.session.commit()

            logger.info(
                "Source system created successfully for company_id=%s",
                company_id,
            )

            return source

        except Exception:
            await self.session.rollback()

            logger.exception(
                "Failed to create source system for company_id=%s",
                company_id,
            )
            raise

    async def list_source_systems(
        self,
        company_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[SourceSystem]:
        """Retrieve a paginated list of source systems for a company."""

        return await self.source_repository.list_by_company(
            company_id,
            limit=limit,
            offset=offset,
        )

    async def get_source_system(
        self,
        source_id: UUID,
    ) -> SourceSystem | None:
        """Retrieve a source system by its ID."""

        return await self.source_repository.get_by_id(source_id)
