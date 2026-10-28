"""Tests for document upload workflow orchestration."""

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.enums import DocumentStatus, UploadAttemptStatus
from app.services.document_upload_service import (
    DocumentReservation,
    ReservationDisposition,
)
from app.services.document_upload_workflow import (
    DocumentUploadFinalizationError,
    DocumentUploadOutcome,
    DocumentUploadOutcomeUncertainError,
    upload_document,
)
from app.storage.document_storage import (
    StoredObjectMetadata,
    build_document_object_key,
)


class AsyncTransaction:
    """Provide an asynchronous transaction context for unit tests."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


def make_session():
    """Create a session mock with an asynchronous transaction context."""
    session = MagicMock()
    session.begin.side_effect = lambda: AsyncTransaction()
    return session


def make_reservation():
    """Create a reserved document and an in-progress upload attempt."""
    document = SimpleNamespace(
        document_id=uuid4(),
        status=DocumentStatus.UPLOADING,
    )
    attempt = SimpleNamespace(
        upload_attempt_id=uuid4(),
        status=UploadAttemptStatus.IN_PROGRESS,
    )

    reservation = DocumentReservation(
        disposition=ReservationDisposition.RESERVED,
        document=document,
        upload_attempt=attempt,
    )

    return reservation, document, attempt


def make_storage(dataset_id, document_id):
    """Create a mock storage adapter and expected stored-object metadata."""
    object_key = build_document_object_key(dataset_id, document_id)

    metadata = StoredObjectMetadata(
        bucket_name="workspace-records",
        object_key=object_key,
        size_bytes=4,
        etag="test-etag",
    )

    storage = MagicMock()
    storage.upload_file = AsyncMock()
    storage.verify_object = AsyncMock(return_value=metadata)

    return storage, metadata


def make_upload_arguments(dataset_id):
    """Build the common arguments supplied to the upload workflow."""
    return {
        "dataset_id": dataset_id,
        "filename": "sample.txt",
        "detected_format": "txt",
        "content_type": "text/plain",
        "file_size_bytes": 4,
        "sha256": "test-sha256",
        "file_obj": BytesIO(b"data"),
    }


@pytest.mark.asyncio
async def test_already_available_document_skips_storage():
    """An existing available document must not be uploaded again."""
    dataset_id = uuid4()
    document = SimpleNamespace(
        document_id=uuid4(),
        status=DocumentStatus.AVAILABLE,
    )

    reservation = DocumentReservation(
        disposition=ReservationDisposition.ALREADY_AVAILABLE,
        document=document,
        upload_attempt=None,
    )

    session = make_session()
    storage = MagicMock()
    session_factory = MagicMock()

    with patch(
        "app.services.document_upload_workflow.reserve_document_upload",
        new=AsyncMock(return_value=reservation),
    ) as reserve_mock:
        result = await upload_document(
            session,
            **make_upload_arguments(dataset_id),
            storage=storage,
            session_factory=session_factory,
        )

    assert result.outcome == DocumentUploadOutcome.ALREADY_AVAILABLE
    assert result.document is document
    reserve_mock.assert_awaited_once()
    storage.upload_file.assert_not_called()


@pytest.mark.asyncio
async def test_successful_upload_finalizes_records_with_row_locks():
    """A verified object should finalize the document and upload attempt."""
    dataset_id = uuid4()
    reservation, document, attempt = make_reservation()

    storage, metadata = make_storage(
        dataset_id,
        document.document_id,
    )
    session = make_session()
    session_factory = MagicMock()

    storage_object = SimpleNamespace(
        storage_object_id=uuid4(),
        document_id=document.document_id,
        verified_at=None,
    )

    document_repository = MagicMock()
    document_repository.get_by_id = AsyncMock(return_value=document)

    async def update_document_status(document_id, status):
        document.status = status
        return document

    document_repository.update_status = AsyncMock(
        side_effect=update_document_status,
    )

    attempt_repository = MagicMock()
    attempt_repository.get_by_id = AsyncMock(return_value=attempt)

    async def update_attempt_status(upload_attempt_id, status, **kwargs):
        attempt.status = status
        attempt.completed_at = kwargs.get("completed_at")
        return attempt

    attempt_repository.update_status = AsyncMock(
        side_effect=update_attempt_status,
    )

    storage_repository = MagicMock()
    storage_repository.get_by_bucket_and_key = AsyncMock(
        return_value=storage_object,
    )

    async def update_verified_at(storage_object_id, verified_at):
        storage_object.verified_at = verified_at
        return storage_object

    storage_repository.update_verified_at = AsyncMock(
        side_effect=update_verified_at,
    )

    with (
        patch(
            "app.services.document_upload_workflow.reserve_document_upload",
            new=AsyncMock(return_value=reservation),
        ),
        patch(
            "app.services.document_upload_workflow.DocumentRepository",
            return_value=document_repository,
        ),
        patch(
            "app.services.document_upload_workflow.UploadAttemptRepository",
            return_value=attempt_repository,
        ),
        patch(
            "app.services.document_upload_workflow.StorageObjectRepository",
            return_value=storage_repository,
        ),
    ):
        result = await upload_document(
            session,
            **make_upload_arguments(dataset_id),
            storage=storage,
            session_factory=session_factory,
        )

    assert result.outcome == DocumentUploadOutcome.UPLOADED
    assert result.document is document
    assert result.upload_attempt is attempt
    assert result.storage_object is storage_object

    assert document.status == DocumentStatus.AVAILABLE
    assert attempt.status == UploadAttemptStatus.SUCCEEDED
    assert storage_object.verified_at is not None

    document_repository.get_by_id.assert_awaited_once_with(
        document.document_id,
        for_update=True,
    )
    attempt_repository.get_by_id.assert_awaited_once_with(
        attempt.upload_attempt_id,
        for_update=True,
    )

    storage.upload_file.assert_awaited_once()
    storage.verify_object.assert_awaited_once_with(
        object_key=metadata.object_key,
        expected_size_bytes=4,
    )


@pytest.mark.asyncio
async def test_storage_failure_requests_reconciliation():
    """An uncertain storage failure must request reconciliation."""
    dataset_id = uuid4()
    reservation, document, attempt = make_reservation()

    storage, _ = make_storage(dataset_id, document.document_id)
    storage.upload_file.side_effect = OSError("Simulated storage failure")

    session = make_session()
    session_factory = MagicMock()

    with (
        patch(
            "app.services.document_upload_workflow.reserve_document_upload",
            new=AsyncMock(return_value=reservation),
        ),
        patch(
            "app.services.document_upload_workflow._mark_reconciliation_required",
            new=AsyncMock(),
        ) as reconciliation_mock,
        pytest.raises(DocumentUploadOutcomeUncertainError),
    ):
        await upload_document(
            session,
            **make_upload_arguments(dataset_id),
            storage=storage,
            session_factory=session_factory,
        )

    reconciliation_mock.assert_awaited_once()

    assert reconciliation_mock.await_args.args[0] is session_factory
    assert (
        reconciliation_mock.await_args.kwargs["document_id"]
        == document.document_id
    )
    assert (
        reconciliation_mock.await_args.kwargs["upload_attempt_id"]
        == attempt.upload_attempt_id
    )

    storage.verify_object.assert_not_awaited()


@pytest.mark.asyncio
async def test_finalization_failure_checks_state_and_requests_reconciliation():
    """An unsuccessful finalization check must request reconciliation."""
    dataset_id = uuid4()
    reservation, document, attempt = make_reservation()

    storage, metadata = make_storage(
        dataset_id,
        document.document_id,
    )

    session = make_session()
    session_factory = MagicMock()

    document_repository = MagicMock()
    document_repository.get_by_id = AsyncMock(
        side_effect=RuntimeError("Simulated finalization failure"),
    )

    attempt_repository = MagicMock()
    storage_repository = MagicMock()

    with (
        patch(
            "app.services.document_upload_workflow.reserve_document_upload",
            new=AsyncMock(return_value=reservation),
        ),
        patch(
            "app.services.document_upload_workflow.DocumentRepository",
            return_value=document_repository,
        ),
        patch(
            "app.services.document_upload_workflow.UploadAttemptRepository",
            return_value=attempt_repository,
        ),
        patch(
            "app.services.document_upload_workflow.StorageObjectRepository",
            return_value=storage_repository,
        ),
        patch(
            "app.services.document_upload_workflow._is_upload_finalized",
            new=AsyncMock(return_value=(False, None, None, None)),
        ) as state_check_mock,
        patch(
            "app.services.document_upload_workflow._mark_reconciliation_required",
            new=AsyncMock(),
        ) as reconciliation_mock,
        pytest.raises(DocumentUploadFinalizationError),
    ):
        await upload_document(
            session,
            **make_upload_arguments(dataset_id),
            storage=storage,
            session_factory=session_factory,
        )

    state_check_mock.assert_awaited_once_with(
        session_factory,
        document_id=document.document_id,
        upload_attempt_id=attempt.upload_attempt_id,
        bucket_name=metadata.bucket_name,
        object_key=metadata.object_key,
    )

    reconciliation_mock.assert_awaited_once()
    assert reconciliation_mock.await_args.args[0] is session_factory