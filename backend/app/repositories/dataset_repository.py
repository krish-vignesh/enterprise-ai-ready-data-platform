"""Repository for Dataset persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset


logger = logging.getLogger(__name__)


class DatasetRepository:
    """Provide database access for Dataset records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
        self,
        dataset_id: UUID,
    ) -> Dataset | None:
        """Return a dataset by UUID, or None if not found."""
        try:
            dataset = await self.session.get(Dataset, dataset_id)

            logger.debug(
                "repository.dataset.get_by_id completed dataset_id=%s found=%s",
                dataset_id,
                dataset is not None,
            )

            return dataset

        except Exception:
            logger.exception(
                "repository.dataset.get_by_id failed dataset_id=%s",
                dataset_id,
            )
            raise

    async def get_by_source_and_name(
        self,
        source_id: UUID,
        dataset_name: str,
    ) -> Dataset | None:
        """Return a dataset by source ID and dataset name."""
        statement = select(Dataset).where(
            Dataset.source_id == source_id,
            Dataset.dataset_name == dataset_name,
        )

        try:
            result = await self.session.scalars(statement)
            dataset = result.one_or_none()

            logger.debug(
                "repository.dataset.get_by_source_and_name completed "
                "source_id=%s found=%s",
                source_id,
                dataset is not None,
            )

            return dataset

        except Exception:
            logger.exception(
                "repository.dataset.get_by_source_and_name failed source_id=%s",
                source_id,
            )
            raise

    async def list_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[Dataset]:
        """Return a paginated list of datasets for a source."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(Dataset)
            .where(Dataset.source_id == source_id)
            .order_by(Dataset.created_at, Dataset.dataset_id)
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            datasets = list(result.all())

            logger.debug(
                "repository.dataset.list_by_source completed "
                "source_id=%s limit=%s offset=%s result_count=%s",
                source_id,
                limit,
                offset,
                len(datasets),
            )

            return datasets

        except Exception:
            logger.exception(
                "repository.dataset.list_by_source failed source_id=%s",
                source_id,
            )
            raise

    def add(self, dataset: Dataset) -> Dataset:
        """Stage a dataset for persistence without committing."""
        try:
            self.session.add(dataset)

            logger.debug("repository.dataset.add staged")

            return dataset

        except Exception:
            logger.exception("repository.dataset.add failed")
            raise
