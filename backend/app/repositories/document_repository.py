"""Repository for Document persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.enums import DocumentStatus


logger = logging.getLogger(__name__)


class DocumentRepository:
    """Provide asynchronous database access for Document records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
            self,
            document_id: UUID,
            *,
            for_update: bool = False,
    ) -> Document | None:
        """Get a document by ID, optionally locking its database row."""
        if for_update:
            return await self.session.get(
                Document,
                document_id,
                with_for_update=True,
                populate_existing=True
            )

        return await self.session.get(Document, document_id)

    async def get_by_dataset_and_sha256(
            self,
            dataset_id: UUID,
            sha256: str,
            *,
            for_update: bool = False,
    ) -> Document | None:
        """Return a document matching a dataset and SHA-256 hash.

        Optionally lock the matching row until the current transaction ends.
        """
        statement = select(Document).where(
            Document.dataset_id == dataset_id,
            Document.sha256 == sha256,
        )

        if for_update:
            statement = statement.with_for_update()

        try:
            result = await self.session.scalars(statement)
            document = result.one_or_none()

            logger.debug(
                "repository.document.get_by_dataset_and_sha256 completed "
                "dataset_id=%s found=%s for_update=%s",
                dataset_id,
                document is not None,
                for_update,
            )
            return document

        except Exception:
            logger.exception(
                "repository.document.get_by_dataset_and_sha256 failed "
                "dataset_id=%s",
                dataset_id,
            )
            raise

    async def list_by_dataset(
        self,
        dataset_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[Document]:
        """Return a deterministically ordered, paginated document list."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(Document)
            .where(Document.dataset_id == dataset_id)
            .order_by(Document.created_at, Document.document_id)
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            documents = list(result.all())

            logger.debug(
                "repository.document.list_by_dataset completed "
                "dataset_id=%s limit=%s offset=%s result_count=%s",
                dataset_id,
                limit,
                offset,
                len(documents),
            )
            return documents

        except Exception:
            logger.exception(
                "repository.document.list_by_dataset failed dataset_id=%s",
                dataset_id,
            )
            raise

    def add(self, document: Document) -> Document:
        """Stage a document for persistence without committing."""
        try:
            self.session.add(document)

            logger.debug("repository.document.add staged")
            return document

        except Exception:
            logger.exception("repository.document.add failed")
            raise

    async def update_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
    ) -> Document | None:
        """Stage a document status change without committing."""
        try:
            document = await self.session.get(Document, document_id)

            if document is None:
                logger.debug(
                    "repository.document.update_status not_found document_id=%s",
                    document_id,
                )
                return None

            document.status = status

            logger.debug(
                "repository.document.update_status staged document_id=%s status=%s",
                document_id,
                status,
            )
            return document

        except Exception:
            logger.exception(
                "repository.document.update_status failed document_id=%s",
                document_id,
            )
            raise
