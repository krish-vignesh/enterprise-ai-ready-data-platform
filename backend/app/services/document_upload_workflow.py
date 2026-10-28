"""Coordinate document uploads across PostgreSQL and MinIO."""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import BinaryIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import AsyncSessionLocal

from app.models.document import Document
from app.models.enums import DocumentStatus, UploadAttemptStatus
from app.models.storage_object import StorageObject
from app.models.upload_attempt import UploadAttempt
from app.repositories.document_repository import DocumentRepository
from app.repositories.storage_object_repository import StorageObjectRepository
from app.repositories.upload_attempt_repository import UploadAttemptRepository
from app.services.document_upload_service import (
    DocumentReservation,
    ReservationDisposition,
    reserve_document_upload,
)
from app.storage.document_storage import (
    MinioDocumentStorage,
    build_document_object_key,
)

logger = logging.getLogger(__name__)


class DocumentUploadOutcome(str, Enum):
    """Describe the outcome of a document-upload request."""

    UPLOADED = "UPLOADED"
    ALREADY_AVAILABLE = "ALREADY_AVAILABLE"
    UPLOAD_IN_PROGRESS = "UPLOAD_IN_PROGRESS"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


class DocumentUploadOutcomeUncertainError(RuntimeError):
    """Raised when the storage operation's outcome cannot be confirmed."""


class DocumentUploadFinalizationError(RuntimeError):
    """Raised when the upload cannot be safely finalized in PostgreSQL."""


@dataclass(frozen=True, slots=True)
class DocumentUploadResult:
    """Return the outcome and relevant records for an upload request."""

    outcome: DocumentUploadOutcome
    document: Document
    upload_attempt: UploadAttempt | None
    storage_object: StorageObject | None = None


def _result_from_reservation(
    reservation: DocumentReservation,
) -> DocumentUploadResult | None:
    """Return immediately when the reservation needs no new upload."""

    outcome_by_disposition = {
        ReservationDisposition.ALREADY_AVAILABLE:
            DocumentUploadOutcome.ALREADY_AVAILABLE,
        ReservationDisposition.UPLOAD_IN_PROGRESS:
            DocumentUploadOutcome.UPLOAD_IN_PROGRESS,
        ReservationDisposition.RECONCILIATION_REQUIRED:
            DocumentUploadOutcome.RECONCILIATION_REQUIRED,
    }

    outcome = outcome_by_disposition.get(reservation.disposition)

    if outcome is None:
        return None

    return DocumentUploadResult(
        outcome=outcome,
        document=reservation.document,
        upload_attempt=reservation.upload_attempt,
    )


async def _mark_reconciliation_required(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    document_id: UUID,
    upload_attempt_id: UUID,
    failure_details: str,
) -> None:
    """Record an uncertain outcome using an independent database session."""

    async with session_factory() as recovery_session:
        async with recovery_session.begin():
            document_repository = DocumentRepository(recovery_session)
            attempt_repository = UploadAttemptRepository(recovery_session)

            document = await document_repository.get_by_id(
                document_id,
                for_update=True,
            )
            attempt = await attempt_repository.get_by_id(
                upload_attempt_id,
                for_update=True,
            )

            if document is None or attempt is None:
                raise RuntimeError(
                    "Cannot reconcile the upload because its records are missing."
                )

            # Never downgrade an upload that was already finalized successfully.
            if (
                document.status == DocumentStatus.AVAILABLE
                and attempt.status == UploadAttemptStatus.SUCCEEDED
            ):
                return

            await document_repository.update_status(
                document_id,
                DocumentStatus.RECONCILIATION_REQUIRED,
            )

            # Preserve IN_PROGRESS when the actual storage outcome is uncertain.
            if attempt.status == UploadAttemptStatus.IN_PROGRESS:
                await attempt_repository.update_status(
                    upload_attempt_id,
                    UploadAttemptStatus.IN_PROGRESS,
                    failure_code="STORAGE_OUTCOME_UNCERTAIN",
                    failure_details=failure_details,
                )


async def _is_upload_finalized(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    document_id: UUID,
    upload_attempt_id: UUID,
    bucket_name: str,
    object_key: str,
) -> tuple[bool, Document | None, UploadAttempt | None, StorageObject | None]:
    """Check persisted state using an independent database session."""

    async with session_factory() as recovery_session:
        async with recovery_session.begin():
            document_repository = DocumentRepository(recovery_session)
            attempt_repository = UploadAttemptRepository(recovery_session)
            storage_repository = StorageObjectRepository(recovery_session)

            document = await document_repository.get_by_id(
                document_id,
                for_update=True,
            )
            attempt = await attempt_repository.get_by_id(
                upload_attempt_id,
                for_update=True,
            )
            storage_object = await storage_repository.get_by_bucket_and_key(
                bucket_name,
                object_key,
            )

            finalized = (
                document is not None
                and attempt is not None
                and storage_object is not None
                and document.status == DocumentStatus.AVAILABLE
                and attempt.status == UploadAttemptStatus.SUCCEEDED
                and storage_object.document_id == document_id
                and storage_object.verified_at is not None
            )

            return finalized, document, attempt, storage_object


async def upload_document(
    session: AsyncSession,
    *,
    dataset_id: UUID,
    filename: str,
    detected_format: str,
    content_type: str | None,
    file_size_bytes: int,
    sha256: str,
    file_obj: BinaryIO,
    request_id: str | None = None,
    storage: MinioDocumentStorage | None = None,
    session_factory: async_sessionmaker[AsyncSession] = AsyncSessionLocal,
) -> DocumentUploadResult:
    """Reserve, store, verify, and finalize a document upload.

    The caller must provide a session with no active transaction.
    Reservation and finalization use separate, short database transactions.
    Recovery checks and reconciliation use an independent session factory.
    """

    storage_adapter = storage or MinioDocumentStorage()

    # Phase 1: reserve the document and its upload attempt in PostgreSQL.
    reservation = await reserve_document_upload(
        session,
        dataset_id=dataset_id,
        filename=filename,
        detected_format=detected_format,
        content_type=content_type,
        file_size_bytes=file_size_bytes,
        sha256=sha256,
        request_id=request_id,
    )

    early_result = _result_from_reservation(reservation)

    if early_result is not None:
        return early_result

    if reservation.upload_attempt is None:
        raise RuntimeError("A new reservation must have an upload attempt.")

    document_id = reservation.document.document_id
    attempt_id = reservation.upload_attempt.upload_attempt_id
    object_key = build_document_object_key(dataset_id, document_id)

    # Phase 2: upload and verify outside any PostgreSQL transaction.
    try:
        await storage_adapter.upload_file(
            object_key=object_key,
            file_obj=file_obj,
            file_size_bytes=file_size_bytes,
            content_type=content_type,
        )

        stored_metadata = await storage_adapter.verify_object(
            object_key=object_key,
            expected_size_bytes=file_size_bytes,
        )

    except Exception as exc:
        logger.exception(
            "document_upload.storage_outcome_uncertain document_id=%s "
            "upload_attempt_id=%s",
            document_id,
            attempt_id,
        )

        try:
            await _mark_reconciliation_required(
                session_factory,
                document_id=document_id,
                upload_attempt_id=attempt_id,
                failure_details=(
                    "The storage operation could not be confirmed. "
                    "Reconciliation is required before another upload attempt."
                ),
            )
        except Exception:
            logger.exception(
                "document_upload.reconciliation_recording_failed "
                "document_id=%s upload_attempt_id=%s",
                document_id,
                attempt_id,
            )

        raise DocumentUploadOutcomeUncertainError(
            "The storage outcome could not be confirmed."
        ) from exc

    # Phase 3: atomically finalize the PostgreSQL records.
    verified_at = datetime.now(timezone.utc)
    storage_object: StorageObject | None = None

    try:
        async with session.begin():
            document_repository = DocumentRepository(session)
            attempt_repository = UploadAttemptRepository(session)
            storage_repository = StorageObjectRepository(session)

            document = await document_repository.get_by_id(
                document_id,
                for_update=True,
            )
            attempt = await attempt_repository.get_by_id(
                attempt_id,
                for_update=True,
            )

            if document is None or attempt is None:
                raise RuntimeError(
                    "The reserved document or upload attempt no longer exists."
                )

            # A concurrent reconciliation must not be overwritten.
            if (
                document.status != DocumentStatus.UPLOADING
                or attempt.status != UploadAttemptStatus.IN_PROGRESS
            ):
                raise RuntimeError(
                    "The upload state changed before finalization."
                )

            storage_object = await storage_repository.get_by_bucket_and_key(
                stored_metadata.bucket_name,
                stored_metadata.object_key,
            )

            if storage_object is None:
                storage_object = StorageObject(
                    document_id=document_id,
                    bucket_name=stored_metadata.bucket_name,
                    object_key=stored_metadata.object_key,
                    verified_at=verified_at,
                )
                storage_repository.add(storage_object)
            else:
                if storage_object.document_id != document_id:
                    raise RuntimeError(
                        "The storage key is already registered to another document."
                    )

                storage_object = await storage_repository.update_verified_at(
                    storage_object.storage_object_id,
                    verified_at,
                )

                if storage_object is None:
                    raise RuntimeError(
                        "The existing storage record could not be updated."
                    )

            updated_document = await document_repository.update_status(
                document_id,
                DocumentStatus.AVAILABLE,
            )
            updated_attempt = await attempt_repository.update_status(
                attempt_id,
                UploadAttemptStatus.SUCCEEDED,
                completed_at=verified_at,
            )

            if updated_document is None or updated_attempt is None:
                raise RuntimeError("The upload records could not be finalized.")

        logger.info(
            "document_upload.completed document_id=%s upload_attempt_id=%s",
            document_id,
            attempt_id,
        )

        return DocumentUploadResult(
            outcome=DocumentUploadOutcome.UPLOADED,
            document=updated_document,
            upload_attempt=updated_attempt,
            storage_object=storage_object,
        )

    except Exception as exc:
        logger.exception(
            "document_upload.finalization_failed document_id=%s "
            "upload_attempt_id=%s",
            document_id,
            attempt_id,
        )

        # The database may have committed even if the client saw an error.
        try:
            finalized, document, attempt, persisted_object = (
                await _is_upload_finalized(
                    session_factory,
                    document_id=document_id,
                    upload_attempt_id=attempt_id,
                    bucket_name=stored_metadata.bucket_name,
                    object_key=stored_metadata.object_key,
                )
            )

            if finalized and document is not None and attempt is not None:
                logger.info(
                    "document_upload.finalization_confirmed_after_error "
                    "document_id=%s upload_attempt_id=%s",
                    document_id,
                    attempt_id,
                )
                return DocumentUploadResult(
                    outcome=DocumentUploadOutcome.UPLOADED,
                    document=document,
                    upload_attempt=attempt,
                    storage_object=persisted_object,
                )

        except Exception:
            logger.exception(
                "document_upload.persisted_state_check_failed "
                "document_id=%s upload_attempt_id=%s",
                document_id,
                attempt_id,
            )

        try:
            await _mark_reconciliation_required(
                session_factory,
                document_id=document_id,
                upload_attempt_id=attempt_id,
                failure_details=(
                    "The file was verified in storage, but database finalization "
                    "could not be confirmed. Reconciliation is required."
                ),
            )
        except Exception:
            logger.exception(
                "document_upload.reconciliation_recording_failed "
                "document_id=%s upload_attempt_id=%s",
                document_id,
                attempt_id,
            )

        raise DocumentUploadFinalizationError(
            "The document upload could not be safely finalized."
        ) from exc