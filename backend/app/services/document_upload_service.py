"""Coordinate safe document-upload reservations in PostgreSQL."""

from dataclasses import dataclass
from enum import Enum
import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.document import Document
from app.models.enums import DocumentStatus, UploadAttemptStatus

from app.models.upload_attempt import UploadAttempt
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.upload_attempt_repository import UploadAttemptRepository


logger = logging.getLogger(__name__)

DOCUMENT_CONTENT_UNIQUE_CONSTRAINT = "uq_documents_dataset_id_sha256"


class DatasetNotFoundError(LookupError):
    """Raised when an upload targets a dataset that does not exist."""


class ReservationDisposition(str, Enum):
    """Describe the outcome of a document reservation request."""

    RESERVED = "RESERVED"
    ALREADY_AVAILABLE = "ALREADY_AVAILABLE"
    UPLOAD_IN_PROGRESS = "UPLOAD_IN_PROGRESS"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


@dataclass(frozen=True, slots=True)
class DocumentReservation:
    """Return the document and attempt associated with a reservation."""

    disposition: ReservationDisposition
    document: Document
    upload_attempt: UploadAttempt | None


def _get_constraint_name(error: IntegrityError) -> str | None:
    """Return the database constraint name when the driver exposes it."""
    original_error = error.orig
    diagnostic = getattr(original_error, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)

    if isinstance(constraint_name, str):
        return constraint_name

    return None


async def _resolve_existing_document(
    *,
    document: Document,
    upload_attempt_repository: UploadAttemptRepository,
    request_id: str | None,
) -> DocumentReservation:
    """Resolve an existing document while its row is locked by the caller."""
    if document.status == DocumentStatus.AVAILABLE:
        return DocumentReservation(
            disposition=ReservationDisposition.ALREADY_AVAILABLE,
            document=document,
            upload_attempt=None,
        )

    if document.status == DocumentStatus.RECONCILIATION_REQUIRED:
        return DocumentReservation(
            disposition=ReservationDisposition.RECONCILIATION_REQUIRED,
            document=document,
            upload_attempt=None,
        )

    latest_attempt = await upload_attempt_repository.get_latest_by_document(
        document.document_id
    )

    if document.status == DocumentStatus.UPLOADING:
        if (
            latest_attempt is not None
            and latest_attempt.status == UploadAttemptStatus.IN_PROGRESS
        ):
            return DocumentReservation(
                disposition=ReservationDisposition.UPLOAD_IN_PROGRESS,
                document=document,
                upload_attempt=latest_attempt,
            )

        # UPLOADING without a matching active attempt is inconsistent state.
        document.status = DocumentStatus.RECONCILIATION_REQUIRED
        logger.warning(
            "document_upload.reservation_inconsistent_state document_id=%s status=%s",
            document.document_id,
            document.status,
        )
        return DocumentReservation(
            disposition=ReservationDisposition.RECONCILIATION_REQUIRED,
            document=document,
            upload_attempt=latest_attempt,
        )

    if document.status == DocumentStatus.FAILED:
        if (
            latest_attempt is None
            or latest_attempt.status != UploadAttemptStatus.FAILED
        ):
            document.status = DocumentStatus.RECONCILIATION_REQUIRED
            logger.warning(
                "document_upload.retry_blocked_for_reconciliation document_id=%s",
                document.document_id,
            )
            return DocumentReservation(
                disposition=ReservationDisposition.RECONCILIATION_REQUIRED,
                document=document,
                upload_attempt=latest_attempt,
            )

        next_attempt = UploadAttempt(
            document_id=document.document_id,
            attempt_number=latest_attempt.attempt_number + 1,
            status=UploadAttemptStatus.IN_PROGRESS,
            request_id=request_id,
        )
        document.status = DocumentStatus.UPLOADING
        upload_attempt_repository.add(next_attempt)

        logger.info(
            "document_upload.retry_reserved document_id=%s attempt_number=%s",
            document.document_id,
            next_attempt.attempt_number,
        )
        return DocumentReservation(
            disposition=ReservationDisposition.RESERVED,
            document=document,
            upload_attempt=next_attempt,
        )

    # Defensive fallback if a new status is added in the future.
    document.status = DocumentStatus.RECONCILIATION_REQUIRED
    return DocumentReservation(
        disposition=ReservationDisposition.RECONCILIATION_REQUIRED,
        document=document,
        upload_attempt=latest_attempt,
    )


async def reserve_document_upload(
    session: AsyncSession,
    *,
    dataset_id: UUID,
    filename: str,
    detected_format: str,
    content_type: str | None,
    file_size_bytes: int,
    sha256: str,
    request_id: str | None = None,
) -> DocumentReservation:
    """Reserve a document and its upload attempt in a short DB transaction.

    The caller must validate upload metadata and calculate SHA-256 before
    calling this function. This function owns its transaction boundaries;
    call it with a session that has no active transaction.

    No MinIO or other network operation is performed here.
    """
    dataset_repository = DatasetRepository(session)
    document_repository = DocumentRepository(session)
    upload_attempt_repository = UploadAttemptRepository(session)


    try:
        async with session.begin():
            dataset = await dataset_repository.get_by_id(dataset_id)

            if dataset is None:
                raise DatasetNotFoundError(f"Dataset '{dataset_id}' does not exist.")

            existing_document = await document_repository.get_by_dataset_and_sha256(
                dataset_id,
                sha256,
                for_update=True,
            )

            if existing_document is not None:
                reservation = await _resolve_existing_document(
                    document=existing_document,
                    upload_attempt_repository=upload_attempt_repository,
                    request_id=request_id,
                )
                await session.flush()
                return reservation

            document = Document(
                dataset_id=dataset_id,
                original_filename=filename,
                detected_format=detected_format,
                content_type=content_type,
                file_size_bytes=file_size_bytes,
                sha256=sha256,
                status=DocumentStatus.UPLOADING,
            )
            document_repository.add(document)

            # Generate/apply database-side Python defaults before using document_id.
            await session.flush()

            upload_attempt = UploadAttempt(
                document_id=document.document_id,
                attempt_number=1,
                status=UploadAttemptStatus.IN_PROGRESS,
                request_id=request_id,
            )
            upload_attempt_repository.add(upload_attempt)

            # Flush the attempt so any constraint violation occurs inside this transaction.
            await session.flush()

            logger.info(
                "document_upload.reservation_created "
                "dataset_id=%s document_id=%s attempt_number=1",
                dataset_id,
                document.document_id,
            )

            return DocumentReservation(
                disposition=ReservationDisposition.RESERVED,
                document=document,
                upload_attempt=upload_attempt,
            )

    except IntegrityError as error:
        # A competing request may have inserted the same dataset/hash pair.
        # Only handle that specific uniqueness race; re-raise other database
        # integrity failures instead of disguising them as duplicate uploads.
        if _get_constraint_name(error) != DOCUMENT_CONTENT_UNIQUE_CONSTRAINT:
            raise

        logger.info(
            "document_upload.concurrent_duplicate_detected dataset_id=%s",
            dataset_id,
        )

        # The failed transaction has been rolled back by session.begin().
        # Re-read the winner in a fresh transaction and resolve its state.
        async with session.begin():
            existing_document = await document_repository.get_by_dataset_and_sha256(
                dataset_id,
                sha256,
                for_update=True,
            )

            if existing_document is None:
                # The error was not a resolvable duplicate after all.
                raise error

            reservation = await _resolve_existing_document(
                document=existing_document,
                upload_attempt_repository=upload_attempt_repository,
                request_id=request_id,
            )
            await session.flush()
            return reservation
