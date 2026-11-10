"""Orchestrate sequential uploads of multiple documents into a dataset."""

import asyncio
from pathlib import PurePath
from typing import Sequence

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.repositories.dataset_repository import DatasetRepository
from app.schemas.document_upload import (
    BatchDocumentUploadItemResponse,
    BatchDocumentUploadResponse,
    DocumentResponse,
)
from app.services.document_upload_service import DatasetNotFoundError
from app.services.document_upload_workflow import (
    DocumentUploadFinalizationError,
    DocumentUploadOutcome,
    DocumentUploadOutcomeUncertainError,
    upload_document,
)
from app.utils.hashing import calculate_sha256
from app.validation.document_upload import (
    DocumentTooLargeError,
    InvalidDocumentFilenameError,
    InvalidDocumentSizeError,
    UnsupportedDocumentFormatError,
    validate_document_upload_metadata,
)


class EmptyDocumentBatchError(ValueError):
    """Raised when a batch contains no files."""


class TooManyDocumentsInBatchError(ValueError):
    """Raised when a batch exceeds the configured file-count limit."""


class DocumentBatchTooLargeError(ValueError):
    """Raised when the aggregate batch size exceeds its configured limit."""


def _build_batch_response(
    results: list[BatchDocumentUploadItemResponse],
) -> BatchDocumentUploadResponse:
    """Calculate batch summary counts from individual file results."""

    counts = {
        "successful_uploads": 0,
        "already_available": 0,
        "in_progress": 0,
        "reconciliation_required": 0,
        "failed_uploads": 0,
    }

    outcome_to_count = {
        DocumentUploadOutcome.UPLOADED: "successful_uploads",
        DocumentUploadOutcome.ALREADY_AVAILABLE: "already_available",
        DocumentUploadOutcome.UPLOAD_IN_PROGRESS: "in_progress",
        DocumentUploadOutcome.RECONCILIATION_REQUIRED: "reconciliation_required",
        "FAILED": "failed_uploads",
    }

    for result in results:
        counts[outcome_to_count[result.outcome]] += 1

    return BatchDocumentUploadResponse(
        total_files=len(results),
        results=results,
        **counts,
    )


async def upload_documents_batch(
    session: AsyncSession,
    *,
    dataset_id,
    files: Sequence[UploadFile],
    request_id: str | None = None,
) -> BatchDocumentUploadResponse:
    """Validate and upload multiple documents sequentially.

    Batch-level validation and dataset preflight happen before any upload.
    Individual file failures are recorded without stopping other uploads.
    """

    # ---------------------------------------------------------
    # 1. Validate batch-level file count
    # ---------------------------------------------------------

    if not files:
        raise EmptyDocumentBatchError("At least one file must be provided.")

    if len(files) > settings.max_batch_upload_files:
        raise TooManyDocumentsInBatchError(
            f"A batch cannot contain more than {settings.max_batch_upload_files} files."
        )

    # ---------------------------------------------------------
    # 2. Measure all files and validate aggregate batch size
    # ---------------------------------------------------------

    measured_files: list[tuple[int, UploadFile, str, int]] = []
    total_size_bytes = 0

    for file_index, file in enumerate(files, start=1):
        filename = file.filename or ""

        # Measure without loading the entire file into memory.
        file.file.seek(0, 2)
        file_size_bytes = file.file.tell()
        file.file.seek(0)

        total_size_bytes += file_size_bytes

        measured_files.append((file_index, file, filename, file_size_bytes))

    if total_size_bytes > settings.max_batch_upload_size_bytes:
        raise DocumentBatchTooLargeError(
            "The combined file size exceeds the maximum allowed "
            f"batch size of {settings.max_batch_upload_size_bytes} bytes."
        )

    # ---------------------------------------------------------
    # 3. Verify dataset existence before processing any file
    # ---------------------------------------------------------

    async with session.begin():
        dataset_repository = DatasetRepository(session)
        dataset = await dataset_repository.get_by_id(dataset_id)

        if dataset is None:
            raise DatasetNotFoundError(f"Dataset '{dataset_id}' does not exist.")

    # The preflight transaction has now ended.
    # The existing upload workflow can safely manage its own transactions.

    # ---------------------------------------------------------
    # 4. Process each file sequentially
    # ---------------------------------------------------------

    results: list[BatchDocumentUploadItemResponse] = []

    for file_index, file, filename, file_size_bytes in measured_files:
        # 4.1 Validate individual file metadata.
        try:
            validate_document_upload_metadata(
                filename,
                file_size_bytes,
                max_file_size_bytes=settings.max_upload_file_size_bytes,
            )

        except InvalidDocumentFilenameError as exc:
            results.append(
                BatchDocumentUploadItemResponse(
                    file_index=file_index,
                    filename=filename,
                    outcome="FAILED",
                    error_code="INVALID_FILENAME",
                    error_message=str(exc),
                )
            )
            continue

        except UnsupportedDocumentFormatError as exc:
            results.append(
                BatchDocumentUploadItemResponse(
                    file_index=file_index,
                    filename=filename,
                    outcome="FAILED",
                    error_code="UNSUPPORTED_FORMAT",
                    error_message=str(exc),
                )
            )
            continue

        except InvalidDocumentSizeError as exc:
            results.append(
                BatchDocumentUploadItemResponse(
                    file_index=file_index,
                    filename=filename,
                    outcome="FAILED",
                    error_code="INVALID_FILE_SIZE",
                    error_message=str(exc),
                )
            )
            continue

        except DocumentTooLargeError as exc:
            results.append(
                BatchDocumentUploadItemResponse(
                    file_index=file_index,
                    filename=filename,
                    outcome="FAILED",
                    error_code="FILE_TOO_LARGE",
                    error_message=str(exc),
                )
            )
            continue

        # 4.2 Derive format and content type.
        detected_format = PurePath(filename).suffix.lower().lstrip(".")
        content_type = file.content_type

        # 4.3 Calculate SHA-256 without blocking the event loop.
        sha256 = await asyncio.to_thread(
            calculate_sha256,
            file.file,
        )

        # 4.4 Execute the existing single-document workflow.
        try:
            upload_result = await upload_document(
                session,
                dataset_id=dataset_id,
                filename=filename,
                detected_format=detected_format,
                content_type=content_type,
                file_size_bytes=file_size_bytes,
                sha256=sha256,
                file_obj=file.file,
                request_id=request_id,
            )

        except DatasetNotFoundError:
            # The dataset may have been deleted after preflight.
            raise

        except DocumentUploadOutcomeUncertainError as exc:
            results.append(
                BatchDocumentUploadItemResponse(
                    file_index=file_index,
                    filename=filename,
                    outcome=DocumentUploadOutcome.RECONCILIATION_REQUIRED,
                    error_code="STORAGE_OUTCOME_UNCERTAIN",
                    error_message=str(exc),
                )
            )
            continue

        except DocumentUploadFinalizationError as exc:
            results.append(
                BatchDocumentUploadItemResponse(
                    file_index=file_index,
                    filename=filename,
                    outcome=DocumentUploadOutcome.RECONCILIATION_REQUIRED,
                    error_code="UPLOAD_FINALIZATION_FAILED",
                    error_message=str(exc),
                )
            )
            continue

        # 4.5 Convert the workflow result into a batch item.
        upload_attempt_id = (
            upload_result.upload_attempt.upload_attempt_id
            if upload_result.upload_attempt is not None
            else None
        )

        results.append(
            BatchDocumentUploadItemResponse(
                file_index=file_index,
                filename=filename,
                outcome=upload_result.outcome,
                document=DocumentResponse.model_validate(upload_result.document),
                upload_attempt_id=upload_attempt_id,
            )
        )

    # ---------------------------------------------------------
    # 5. Build the final batch summary
    # ---------------------------------------------------------

    return _build_batch_response(results)
