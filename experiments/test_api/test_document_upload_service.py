
"""Tests for document-upload reservation decisions and service orchestration."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.document_upload_service as service_module
from app.models.enums import DocumentStatus, UploadAttemptStatus
from app.models.upload_attempt import UploadAttempt
from app.services.document_upload_service import (
    DatasetNotFoundError,
    ReservationDisposition,
    _resolve_existing_document,
    reserve_document_upload,
)


@pytest.fixture
def upload_attempt_repository():
    repository = MagicMock()
    repository.get_latest_by_document = AsyncMock(return_value=None)
    return repository


@pytest.fixture
def document():
    return SimpleNamespace(
        document_id=uuid4(),
        status=DocumentStatus.AVAILABLE,
    )


def make_mock_session():
    """Create a mocked async session with a transaction context."""
    session = MagicMock(spec=AsyncSession)

    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=None)
    transaction.__aexit__ = AsyncMock(return_value=False)

    session.begin.return_value = transaction
    session.flush = AsyncMock()

    return session


@pytest.mark.asyncio
async def test_available_document_is_reused(
    document,
    upload_attempt_repository,
):
    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=None,
    )

    assert result.disposition == ReservationDisposition.ALREADY_AVAILABLE
    assert result.document is document
    assert result.upload_attempt is None
    upload_attempt_repository.get_latest_by_document.assert_not_awaited()


@pytest.mark.asyncio
async def test_reconciliation_required_document_is_blocked(
    document,
    upload_attempt_repository,
):
    document.status = DocumentStatus.RECONCILIATION_REQUIRED

    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=None,
    )

    assert (
        result.disposition
        == ReservationDisposition.RECONCILIATION_REQUIRED
    )
    assert result.document is document
    assert result.upload_attempt is None
    upload_attempt_repository.get_latest_by_document.assert_not_awaited()


@pytest.mark.asyncio
async def test_active_upload_is_not_reserved_twice(
    document,
    upload_attempt_repository,
):
    document.status = DocumentStatus.UPLOADING
    active_attempt = SimpleNamespace(
        status=UploadAttemptStatus.IN_PROGRESS,
        attempt_number=1,
    )
    upload_attempt_repository.get_latest_by_document.return_value = (
        active_attempt
    )

    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=None,
    )

    assert result.disposition == ReservationDisposition.UPLOAD_IN_PROGRESS
    assert result.upload_attempt is active_attempt


@pytest.mark.asyncio
async def test_uploading_document_without_active_attempt_requires_reconciliation(
    document,
    upload_attempt_repository,
):
    document.status = DocumentStatus.UPLOADING
    upload_attempt_repository.get_latest_by_document.return_value = None

    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=None,
    )

    assert (
        result.disposition
        == ReservationDisposition.RECONCILIATION_REQUIRED
    )
    assert document.status == DocumentStatus.RECONCILIATION_REQUIRED


@pytest.mark.asyncio
async def test_failed_attempt_can_be_retried(
    document,
    upload_attempt_repository,
):
    document.status = DocumentStatus.FAILED
    previous_attempt = SimpleNamespace(
        attempt_number=2,
        status=UploadAttemptStatus.FAILED,
    )
    upload_attempt_repository.get_latest_by_document.return_value = (
        previous_attempt
    )
    upload_attempt_repository.add = MagicMock()
    request_id = "test-request-123"

    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=request_id,
    )

    assert result.disposition == ReservationDisposition.RESERVED
    assert document.status == DocumentStatus.UPLOADING
    assert isinstance(result.upload_attempt, UploadAttempt)
    assert result.upload_attempt.attempt_number == 3
    assert result.upload_attempt.request_id == request_id
    assert result.upload_attempt.status == UploadAttemptStatus.IN_PROGRESS
    upload_attempt_repository.add.assert_called_once_with(
        result.upload_attempt
    )


@pytest.mark.asyncio
async def test_failed_document_without_attempt_requires_reconciliation(
    document,
    upload_attempt_repository,
):
    document.status = DocumentStatus.FAILED
    upload_attempt_repository.get_latest_by_document.return_value = None

    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=None,
    )

    assert (
        result.disposition
        == ReservationDisposition.RECONCILIATION_REQUIRED
    )
    assert document.status == DocumentStatus.RECONCILIATION_REQUIRED


@pytest.mark.asyncio
async def test_failed_document_with_nonfailed_attempt_requires_reconciliation(
    document,
    upload_attempt_repository,
):
    document.status = DocumentStatus.FAILED
    previous_attempt = SimpleNamespace(
        attempt_number=1,
        status=UploadAttemptStatus.SUCCEEDED,
    )
    upload_attempt_repository.get_latest_by_document.return_value = (
        previous_attempt
    )

    result = await _resolve_existing_document(
        document=document,
        upload_attempt_repository=upload_attempt_repository,
        request_id=None,
    )

    assert (
        result.disposition
        == ReservationDisposition.RECONCILIATION_REQUIRED
    )
    assert document.status == DocumentStatus.RECONCILIATION_REQUIRED


@pytest.mark.asyncio
async def test_reservation_raises_when_dataset_does_not_exist(
    monkeypatch,
):
    session = make_mock_session()
    dataset_id = uuid4()

    dataset_repository = MagicMock()
    dataset_repository.get_by_id = AsyncMock(return_value=None)

    document_repository = MagicMock()
    document_repository.get_by_dataset_and_sha256 = AsyncMock()

    upload_attempt_repository = MagicMock()

    monkeypatch.setattr(
        service_module,
        "DatasetRepository",
        lambda _session: dataset_repository,
    )
    monkeypatch.setattr(
        service_module,
        "DocumentRepository",
        lambda _session: document_repository,
    )
    monkeypatch.setattr(
        service_module,
        "UploadAttemptRepository",
        lambda _session: upload_attempt_repository,
    )

    with pytest.raises(DatasetNotFoundError):
        await reserve_document_upload(
            session,
            dataset_id=dataset_id,
            filename="sales.csv",
            detected_format="csv",
            content_type="text/csv",
            file_size_bytes=100,
            sha256="a" * 64,
        )

    dataset_repository.get_by_id.assert_awaited_once_with(dataset_id)
    document_repository.get_by_dataset_and_sha256.assert_not_awaited()
    document_repository.add.assert_not_called()
    upload_attempt_repository.add.assert_not_called()
    session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_new_document_reservation_creates_first_attempt(
    monkeypatch,
):
    session = make_mock_session()
    dataset_id = uuid4()
    request_id = "test-request-456"
    sha256 = "b" * 64

    dataset_repository = MagicMock()
    dataset_repository.get_by_id = AsyncMock(return_value=MagicMock())

    document_repository = MagicMock()
    document_repository.get_by_dataset_and_sha256 = AsyncMock(
        return_value=None
    )

    upload_attempt_repository = MagicMock()

    document = MagicMock()
    document.document_id = uuid4()
    document.status = DocumentStatus.UPLOADING

    document_constructor = MagicMock(return_value=document)

    monkeypatch.setattr(
        service_module,
        "DatasetRepository",
        lambda _session: dataset_repository,
    )
    monkeypatch.setattr(
        service_module,
        "DocumentRepository",
        lambda _session: document_repository,
    )
    monkeypatch.setattr(
        service_module,
        "UploadAttemptRepository",
        lambda _session: upload_attempt_repository,
    )
    monkeypatch.setattr(
        service_module,
        "Document",
        document_constructor,
    )

    result = await reserve_document_upload(
        session,
        dataset_id=dataset_id,
        filename="sales.csv",
        detected_format="csv",
        content_type="text/csv",
        file_size_bytes=100,
        sha256=sha256,
        request_id=request_id,
    )

    assert result.disposition == ReservationDisposition.RESERVED
    assert result.document is document
    assert result.document.status == DocumentStatus.UPLOADING

    document_constructor.assert_called_once_with(
        dataset_id=dataset_id,
        original_filename="sales.csv",
        detected_format="csv",
        content_type="text/csv",
        file_size_bytes=100,
        sha256=sha256,
        status=DocumentStatus.UPLOADING,
    )

    document_repository.add.assert_called_once_with(document)

    upload_attempt_repository.add.assert_called_once()
    attempt = upload_attempt_repository.add.call_args.args[0]

    assert attempt.document_id == document.document_id
    assert attempt.attempt_number == 1
    assert attempt.status == UploadAttemptStatus.IN_PROGRESS
    assert attempt.request_id == request_id

    dataset_repository.get_by_id.assert_awaited_once_with(dataset_id)
    document_repository.get_by_dataset_and_sha256.assert_awaited_once_with(
        dataset_id,
        sha256,
        for_update=True,
    )

    assert session.flush.await_count == 2
