"""Repository for UploadAttempt persistence operations."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UploadAttemptStatus
from app.models.upload_attempt import UploadAttempt


logger = logging.getLogger(__name__)


class UploadAttemptRepository:
    """Provide asynchronous database access for upload-attempt records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
            self,
            upload_attempt_id: UUID,
            *,
            for_update: bool = False,
    ) -> UploadAttempt | None:
        """Get an upload attempt by ID, optionally locking its database row."""
        if for_update:
            return await self.session.get(
                UploadAttempt,
                upload_attempt_id,
                with_for_update=True,
                populate_existing=True
            )

        return await self.session.get(UploadAttempt, upload_attempt_id)

    async def update_status(
        self,
        upload_attempt_id: UUID,
        status: UploadAttemptStatus,
        *,
        completed_at: datetime | None = None,
        failure_code: str | None = None,
        failure_details: str | None = None,
    ) -> UploadAttempt | None:
        """Stage supplied status and outcome changes without committing."""
        try:
            upload_attempt = await self.session.get(
                UploadAttempt,
                upload_attempt_id,
            )

            if upload_attempt is None:
                logger.debug(
                    "repository.upload_attempt.update_status not_found "
                    "upload_attempt_id=%s",
                    upload_attempt_id,
                )
                return None

            upload_attempt.status = status

            if completed_at is not None:
                upload_attempt.completed_at = completed_at

            if failure_code is not None:
                upload_attempt.failure_code = failure_code

            if failure_details is not None:
                upload_attempt.failure_details = failure_details

            logger.debug(
                "repository.upload_attempt.update_status staged "
                "upload_attempt_id=%s status=%s",
                upload_attempt_id,
                status,
            )
            return upload_attempt

        except Exception:
            logger.exception(
                "repository.upload_attempt.update_status failed upload_attempt_id=%s",
                upload_attempt_id,
            )
            raise

    async def get_by_document_and_attempt_number(
        self,
        document_id: UUID,
        attempt_number: int,
    ) -> UploadAttempt | None:
        """Return an attempt identified by document and attempt number."""
        if attempt_number < 1:
            raise ValueError("attempt_number must be greater than zero")

        statement = select(UploadAttempt).where(
            UploadAttempt.document_id == document_id,
            UploadAttempt.attempt_number == attempt_number,
        )

        try:
            result = await self.session.scalars(statement)
            upload_attempt = result.one_or_none()

            logger.debug(
                "repository.upload_attempt.get_by_document_and_attempt_number "
                "completed document_id=%s attempt_number=%s found=%s",
                document_id,
                attempt_number,
                upload_attempt is not None,
            )
            return upload_attempt

        except Exception:
            logger.exception(
                "repository.upload_attempt.get_by_document_and_attempt_number "
                "failed document_id=%s attempt_number=%s",
                document_id,
                attempt_number,
            )
            raise

    async def get_latest_by_document(
        self,
        document_id: UUID,
    ) -> UploadAttempt | None:
        """Return the most recent numbered attempt for a document."""
        statement = (
            select(UploadAttempt)
            .where(UploadAttempt.document_id == document_id)
            .order_by(
                UploadAttempt.attempt_number.desc(),
                UploadAttempt.upload_attempt_id.desc(),
            )
            .limit(1)
        )

        try:
            result = await self.session.scalars(statement)
            upload_attempt = result.first()

            logger.debug(
                "repository.upload_attempt.get_latest_by_document completed "
                "document_id=%s found=%s",
                document_id,
                upload_attempt is not None,
            )
            return upload_attempt

        except Exception:
            logger.exception(
                "repository.upload_attempt.get_latest_by_document failed "
                "document_id=%s",
                document_id,
            )
            raise

    async def list_by_document(
        self,
        document_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[UploadAttempt]:
        """Return a paginated list of attempts for a document."""
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        statement = (
            select(UploadAttempt)
            .where(UploadAttempt.document_id == document_id)
            .order_by(
                UploadAttempt.attempt_number,
                UploadAttempt.upload_attempt_id,
            )
            .limit(limit)
            .offset(offset)
        )

        try:
            result = await self.session.scalars(statement)
            attempts = list(result.all())

            logger.debug(
                "repository.upload_attempt.list_by_document completed "
                "document_id=%s limit=%s offset=%s result_count=%s",
                document_id,
                limit,
                offset,
                len(attempts),
            )
            return attempts

        except Exception:
            logger.exception(
                "repository.upload_attempt.list_by_document failed document_id=%s",
                document_id,
            )
            raise

    def add(self, upload_attempt: UploadAttempt) -> UploadAttempt:
        """Stage an upload attempt for persistence without committing."""
        try:
            self.session.add(upload_attempt)

            logger.debug("repository.upload_attempt.add staged")
            return upload_attempt

        except Exception:
            logger.exception("repository.upload_attempt.add failed")
            raise
