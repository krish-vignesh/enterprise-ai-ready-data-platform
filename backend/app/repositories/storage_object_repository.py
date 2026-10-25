"""Repository for StorageObject persistence operations."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.dataset import Dataset
from app.models.document import Document
from app.models.source_system import SourceSystem
from app.models.storage_object import StorageObject


logger = logging.getLogger(__name__)


class StorageObjectRepository:
    """Provide asynchronous database access for storage-object records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
        self,
        storage_object_id: UUID,
    ) -> StorageObject | None:
        """Return a storage object by UUID, or None if it does not exist."""
        try:
            storage_object = await self.session.get(
                StorageObject,
                storage_object_id,
            )

            logger.debug(
                "repository.storage_object.get_by_id completed "
                "storage_object_id=%s found=%s",
                storage_object_id,
                storage_object is not None,
            )
            return storage_object

        except Exception:
            logger.exception(
                "repository.storage_object.get_by_id failed storage_object_id=%s",
                storage_object_id,
            )
            raise

    async def get_by_bucket_and_key(
        self,
        bucket_name: str,
        object_key: str,
    ) -> StorageObject | None:
        """Return a storage object by its unique bucket and object key."""
        statement = select(StorageObject).where(
            StorageObject.bucket_name == bucket_name,
            StorageObject.object_key == object_key,
        )

        try:
            result = await self.session.scalars(statement)
            storage_object = result.one_or_none()

            logger.debug(
                "repository.storage_object.get_by_bucket_and_key completed "
                "bucket_name=%s found=%s",
                bucket_name,
                storage_object is not None,
            )
            return storage_object

        except Exception:
            logger.exception(
                "repository.storage_object.get_by_bucket_and_key failed bucket_name=%s",
                bucket_name,
            )
            raise

    async def list_by_document(
        self,
        document_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[StorageObject]:
        """Return a paginated list of storage objects for a document."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(StorageObject)
            .where(StorageObject.document_id == document_id)
            .order_by(
                StorageObject.created_at,
                StorageObject.storage_object_id,
            )
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            storage_objects = list(result.all())

            logger.debug(
                "repository.storage_object.list_by_document completed "
                "document_id=%s limit=%s offset=%s result_count=%s",
                document_id,
                limit,
                offset,
                len(storage_objects),
            )
            return storage_objects

        except Exception:
            logger.exception(
                "repository.storage_object.list_by_document failed document_id=%s",
                document_id,
            )
            raise

    async def list_by_company(
        self,
        company_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[StorageObject]:
        """Return storage objects belonging to a company's documents."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(StorageObject)
            .join(
                Document,
                StorageObject.document_id == Document.document_id,
            )
            .join(
                Dataset,
                Document.dataset_id == Dataset.dataset_id,
            )
            .join(
                SourceSystem,
                Dataset.source_id == SourceSystem.source_id,
            )
            .join(
                Company,
                SourceSystem.company_id == Company.company_id,
            )
            .where(Company.company_id == company_id)
            .order_by(
                StorageObject.created_at,
                StorageObject.storage_object_id,
            )
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            storage_objects = list(result.all())

            logger.debug(
                "repository.storage_object.list_by_company completed "
                "company_id=%s limit=%s offset=%s result_count=%s",
                company_id,
                limit,
                offset,
                len(storage_objects),
            )
            return storage_objects

        except Exception:
            logger.exception(
                "repository.storage_object.list_by_company failed company_id=%s",
                company_id,
            )
            raise

    def add(self, storage_object: StorageObject) -> StorageObject:
        """Stage a storage object for persistence without committing."""
        try:
            self.session.add(storage_object)

            logger.debug("repository.storage_object.add staged")
            return storage_object

        except Exception:
            logger.exception("repository.storage_object.add failed")
            raise

    async def update_verified_at(
        self,
        storage_object_id: UUID,
        verified_at: datetime | None,
    ) -> StorageObject | None:
        """Stage a storage verification timestamp update without committing."""
        try:
            storage_object = await self.session.get(
                StorageObject,
                storage_object_id,
            )

            if storage_object is None:
                logger.debug(
                    "repository.storage_object.update_verified_at not_found "
                    "storage_object_id=%s",
                    storage_object_id,
                )
                return None

            storage_object.verified_at = verified_at

            logger.debug(
                "repository.storage_object.update_verified_at staged "
                "storage_object_id=%s",
                storage_object_id,
            )
            return storage_object

        except Exception:
            logger.exception(
                "repository.storage_object.update_verified_at failed "
                "storage_object_id=%s",
                storage_object_id,
            )
            raise
