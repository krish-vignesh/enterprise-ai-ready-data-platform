"""Unit tests for all six repositories using a mocked AsyncSession."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.dataset import Dataset
from app.models.document import Document
from app.models.source_system import SourceSystem
from app.models.storage_object import StorageObject
from app.models.upload_attempt import UploadAttempt, UploadAttemptStatus

from app.repositories.company_repository import CompanyRepository
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceSystemRepository
from app.repositories.storage_object_repository import StorageObjectRepository
from app.repositories.upload_attempt_repository import UploadAttemptRepository


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def session():
    """Provide a mocked asynchronous SQLAlchemy session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def company_repository(session):
    return CompanyRepository(session)


@pytest.fixture
def source_repository(session):
    return SourceSystemRepository(session)


@pytest.fixture
def dataset_repository(session):
    return DatasetRepository(session)


@pytest.fixture
def document_repository(session):
    return DocumentRepository(session)


@pytest.fixture
def storage_object_repository(session):
    return StorageObjectRepository(session)


@pytest.fixture
def upload_attempt_repository(session):
    return UploadAttemptRepository(session)


def configure_scalar_result(session, *, one=None, all=None):
    """Configure the result returned by an awaited session.scalars() call."""
    result = MagicMock()
    result.one_or_none.return_value = one
    result.all.return_value = [] if all is None else all
    session.scalars.return_value = result
    return result


# ---------------------------------------------------------------------------
# CompanyRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_company_get_by_id_returns_company(session, company_repository):
    company_id = uuid4()
    expected = MagicMock(spec=Company)
    session.get.return_value = expected

    result = await company_repository.get_by_id(company_id)

    session.get.assert_awaited_once_with(Company, company_id)
    assert result is expected


@pytest.mark.asyncio
async def test_company_get_by_id_returns_none_when_missing(session, company_repository):
    session.get.return_value = None

    result = await company_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_company_list_paginated_returns_companies(session, company_repository):
    expected = [MagicMock(spec=Company), MagicMock(spec=Company)]
    configure_scalar_result(session, all=expected)

    result = await company_repository.list_paginated(limit=10, offset=5)

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_company_list_paginated_rejects_zero_limit(company_repository):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await company_repository.list_paginated(limit=0)


@pytest.mark.asyncio
async def test_company_list_paginated_rejects_negative_offset(
    company_repository,
):
    with pytest.raises(ValueError, match="offset cannot be negative"):
        await company_repository.list_paginated(limit=10, offset=-1)


def test_company_add_stages_without_committing(session, company_repository):
    company = MagicMock(spec=Company)

    result = company_repository.add(company)

    session.add.assert_called_once_with(company)
    session.commit.assert_not_called()
    assert result is company


# ---------------------------------------------------------------------------
# SourceSystemRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_source_get_by_id_returns_source(session, source_repository):
    source_id = uuid4()
    expected = MagicMock(spec=SourceSystem)
    session.get.return_value = expected

    result = await source_repository.get_by_id(source_id)

    session.get.assert_awaited_once_with(SourceSystem, source_id)
    assert result is expected


@pytest.mark.asyncio
async def test_source_get_by_id_returns_none_when_missing(session, source_repository):
    session.get.return_value = None

    result = await source_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_source_list_by_company_returns_sources(session, source_repository):
    company_id = uuid4()
    expected = [MagicMock(spec=SourceSystem), MagicMock(spec=SourceSystem)]
    configure_scalar_result(session, all=expected)

    result = await source_repository.list_by_company(company_id, limit=10, offset=5)

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_source_list_by_company_rejects_zero_limit(source_repository):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await source_repository.list_by_company(uuid4(), limit=0)


@pytest.mark.asyncio
async def test_source_list_by_company_rejects_negative_offset(
    source_repository,
):
    with pytest.raises(ValueError, match="offset cannot be negative"):
        await source_repository.list_by_company(uuid4(), limit=10, offset=-1)


def test_source_add_stages_without_committing(session, source_repository):
    source = MagicMock(spec=SourceSystem)

    result = source_repository.add(source)

    session.add.assert_called_once_with(source)
    session.commit.assert_not_called()
    assert result is source


# ---------------------------------------------------------------------------
# DatasetRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dataset_get_by_id_returns_dataset(session, dataset_repository):
    dataset_id = uuid4()
    expected = MagicMock(spec=Dataset)
    session.get.return_value = expected

    result = await dataset_repository.get_by_id(dataset_id)

    session.get.assert_awaited_once_with(Dataset, dataset_id)
    assert result is expected


@pytest.mark.asyncio
async def test_dataset_get_by_id_returns_none_when_missing(session, dataset_repository):
    session.get.return_value = None

    result = await dataset_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_dataset_get_by_source_and_name_returns_dataset(
    session, dataset_repository
):
    source_id = uuid4()
    expected = MagicMock(spec=Dataset)
    scalar_result = configure_scalar_result(session, one=expected)

    result = await dataset_repository.get_by_source_and_name(source_id, "sales")

    session.scalars.assert_awaited_once()
    scalar_result.one_or_none.assert_called_once_with()
    assert result is expected


@pytest.mark.asyncio
async def test_dataset_list_by_source_returns_datasets(session, dataset_repository):
    source_id = uuid4()
    expected = [MagicMock(spec=Dataset), MagicMock(spec=Dataset)]
    configure_scalar_result(session, all=expected)

    result = await dataset_repository.list_by_source(source_id, limit=10, offset=5)

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_dataset_list_by_source_rejects_zero_limit(
    dataset_repository,
):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await dataset_repository.list_by_source(uuid4(), limit=0)


@pytest.mark.asyncio
async def test_dataset_list_by_source_rejects_negative_offset(
    dataset_repository,
):
    with pytest.raises(ValueError, match="offset cannot be negative"):
        await dataset_repository.list_by_source(uuid4(), limit=10, offset=-1)


def test_dataset_add_stages_without_committing(session, dataset_repository):
    dataset = MagicMock(spec=Dataset)

    result = dataset_repository.add(dataset)

    session.add.assert_called_once_with(dataset)
    session.commit.assert_not_called()
    assert result is dataset


# ---------------------------------------------------------------------------
# DocumentRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_document_get_by_id_returns_document(session, document_repository):
    document_id = uuid4()
    expected = MagicMock(spec=Document)
    session.get.return_value = expected

    result = await document_repository.get_by_id(document_id)

    session.get.assert_awaited_once_with(Document, document_id)
    assert result is expected


@pytest.mark.asyncio
async def test_document_get_by_id_returns_none_when_missing(
    session, document_repository
):
    session.get.return_value = None

    result = await document_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_document_get_by_dataset_and_sha256_returns_document(
    session, document_repository
):
    dataset_id = uuid4()
    file_hash = "a" * 64
    expected = MagicMock(spec=Document)
    scalar_result = configure_scalar_result(session, one=expected)

    result = await document_repository.get_by_dataset_and_sha256(dataset_id, file_hash)

    session.scalars.assert_awaited_once()
    scalar_result.one_or_none.assert_called_once_with()
    assert result is expected


@pytest.mark.asyncio
async def test_document_list_by_dataset_returns_documents(session, document_repository):
    dataset_id = uuid4()
    expected = [MagicMock(spec=Document), MagicMock(spec=Document)]
    configure_scalar_result(session, all=expected)

    result = await document_repository.list_by_dataset(dataset_id, limit=10, offset=5)

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_document_list_by_dataset_rejects_zero_limit(
    document_repository,
):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await document_repository.list_by_dataset(uuid4(), limit=0)


@pytest.mark.asyncio
async def test_document_list_by_dataset_rejects_negative_offset(
    document_repository,
):
    with pytest.raises(ValueError, match="offset cannot be negative"):
        await document_repository.list_by_dataset(uuid4(), limit=10, offset=-1)


def test_document_add_stages_without_committing(session, document_repository):
    document = MagicMock(spec=Document)

    result = document_repository.add(document)

    session.add.assert_called_once_with(document)
    session.commit.assert_not_called()
    assert result is document


@pytest.mark.asyncio
async def test_document_update_status_updates_existing_document(
    session, document_repository
):
    document_id = uuid4()
    document = MagicMock(spec=Document)
    session.get.return_value = document
    new_status = "AVAILABLE"

    result = await document_repository.update_status(document_id, new_status)

    session.get.assert_awaited_once_with(Document, document_id)
    assert document.status == new_status
    assert result is document
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_document_update_status_returns_none_when_missing(
    session, document_repository
):
    session.get.return_value = None

    result = await document_repository.update_status(uuid4(), "AVAILABLE")

    assert result is None


# ---------------------------------------------------------------------------
# StorageObjectRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_storage_object_get_by_id_returns_object(
    session, storage_object_repository
):
    storage_object_id = uuid4()
    expected = MagicMock(spec=StorageObject)
    session.get.return_value = expected

    result = await storage_object_repository.get_by_id(storage_object_id)

    session.get.assert_awaited_once_with(StorageObject, storage_object_id)
    assert result is expected


@pytest.mark.asyncio
async def test_storage_object_get_by_id_returns_none_when_missing(
    session, storage_object_repository
):
    session.get.return_value = None

    result = await storage_object_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_storage_object_get_by_bucket_and_key_returns_object(
    session, storage_object_repository
):
    expected = MagicMock(spec=StorageObject)
    scalar_result = configure_scalar_result(session, one=expected)

    result = await storage_object_repository.get_by_bucket_and_key(
        "ai-data", "bronze/file.parquet"
    )

    session.scalars.assert_awaited_once()
    scalar_result.one_or_none.assert_called_once_with()
    assert result is expected


@pytest.mark.asyncio
async def test_storage_object_list_by_document_returns_objects(
    session, storage_object_repository
):
    document_id = uuid4()
    expected = [MagicMock(spec=StorageObject)]
    configure_scalar_result(session, all=expected)

    result = await storage_object_repository.list_by_document(
        document_id, limit=10, offset=0
    )

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_storage_object_list_by_document_rejects_invalid_pagination(
    storage_object_repository,
):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await storage_object_repository.list_by_document(uuid4(), limit=0)

    with pytest.raises(ValueError, match="offset cannot be negative"):
        await storage_object_repository.list_by_document(uuid4(), limit=10, offset=-1)


@pytest.mark.asyncio
async def test_storage_object_list_by_company_returns_objects(
    session, storage_object_repository
):
    company_id = uuid4()
    expected = [MagicMock(spec=StorageObject)]
    configure_scalar_result(session, all=expected)

    result = await storage_object_repository.list_by_company(
        company_id, limit=10, offset=0
    )

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_storage_object_list_by_company_rejects_invalid_pagination(
    storage_object_repository,
):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await storage_object_repository.list_by_company(uuid4(), limit=0)

    with pytest.raises(ValueError, match="offset cannot be negative"):
        await storage_object_repository.list_by_company(uuid4(), limit=10, offset=-1)


def test_storage_object_add_stages_without_committing(
    session, storage_object_repository
):
    storage_object = MagicMock(spec=StorageObject)

    result = storage_object_repository.add(storage_object)

    session.add.assert_called_once_with(storage_object)
    session.commit.assert_not_called()
    assert result is storage_object


@pytest.mark.asyncio
async def test_storage_object_update_verified_at_updates_existing_object(
    session, storage_object_repository
):
    storage_object_id = uuid4()
    storage_object = MagicMock(spec=StorageObject)
    verified_at = datetime.now(UTC)
    session.get.return_value = storage_object

    result = await storage_object_repository.update_verified_at(
        storage_object_id, verified_at
    )

    session.get.assert_awaited_once_with(StorageObject, storage_object_id)
    assert storage_object.verified_at == verified_at
    assert result is storage_object
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_storage_object_update_verified_at_returns_none_when_missing(
    session, storage_object_repository
):
    session.get.return_value = None

    result = await storage_object_repository.update_verified_at(
        uuid4(), datetime.now(UTC)
    )

    assert result is None


# ---------------------------------------------------------------------------
# UploadAttemptRepository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upload_attempt_get_by_id_returns_attempt(
    session, upload_attempt_repository
):
    attempt_id = uuid4()
    expected = MagicMock(spec=UploadAttempt)
    session.get.return_value = expected

    result = await upload_attempt_repository.get_by_id(attempt_id)

    session.get.assert_awaited_once_with(UploadAttempt, attempt_id)
    assert result is expected


@pytest.mark.asyncio
async def test_upload_attempt_get_by_id_returns_none_when_missing(
    session, upload_attempt_repository
):
    session.get.return_value = None

    result = await upload_attempt_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_upload_attempt_get_by_document_and_number(
    session, upload_attempt_repository
):
    document_id = uuid4()
    expected = MagicMock(spec=UploadAttempt)
    scalar_result = configure_scalar_result(session, one=expected)

    result = await upload_attempt_repository.get_by_document_and_attempt_number(
        document_id, 1
    )

    session.scalars.assert_awaited_once()
    scalar_result.one_or_none.assert_called_once_with()
    assert result is expected


@pytest.mark.asyncio
async def test_upload_attempt_rejects_invalid_attempt_number(
    upload_attempt_repository,
):
    with pytest.raises(ValueError):
        await upload_attempt_repository.get_by_document_and_attempt_number(uuid4(), 0)


@pytest.mark.asyncio
async def test_upload_attempt_get_latest_by_document(
    session, upload_attempt_repository
):
    document_id = uuid4()
    expected = MagicMock(spec=UploadAttempt)

    scalar_result = MagicMock()
    scalar_result.first.return_value = expected
    session.scalars.return_value = scalar_result

    result = await upload_attempt_repository.get_latest_by_document(document_id)

    session.scalars.assert_awaited_once()
    scalar_result.first.assert_called_once_with()
    assert result is expected


@pytest.mark.asyncio
async def test_upload_attempt_list_by_document_returns_attempts(
    session, upload_attempt_repository
):
    document_id = uuid4()
    expected = [MagicMock(spec=UploadAttempt)]
    configure_scalar_result(session, all=expected)

    result = await upload_attempt_repository.list_by_document(
        document_id, limit=10, offset=0
    )

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_upload_attempt_list_by_document_rejects_invalid_pagination(
    upload_attempt_repository,
):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await upload_attempt_repository.list_by_document(uuid4(), limit=0)

    with pytest.raises(ValueError, match="offset cannot be negative"):
        await upload_attempt_repository.list_by_document(uuid4(), limit=10, offset=-1)


def test_upload_attempt_add_stages_without_committing(
    session, upload_attempt_repository
):
    attempt = MagicMock(spec=UploadAttempt)

    result = upload_attempt_repository.add(attempt)

    session.add.assert_called_once_with(attempt)
    session.commit.assert_not_called()
    assert result is attempt


@pytest.mark.asyncio
async def test_upload_attempt_update_status_preserves_omitted_fields(
    session, upload_attempt_repository
):
    attempt_id = uuid4()
    attempt = MagicMock(spec=UploadAttempt)
    attempt.status = UploadAttemptStatus.FAILED
    attempt.completed_at = datetime(2026, 1, 1, tzinfo=UTC)
    attempt.failure_code = "UPLOAD_FAILED"
    attempt.failure_details = "Original failure details"
    session.get.return_value = attempt

    result = await upload_attempt_repository.update_status(
        attempt_id,
        UploadAttemptStatus.SUCCEEDED,
    )

    assert result is attempt
    assert attempt.status == UploadAttemptStatus.SUCCEEDED
    assert attempt.completed_at == datetime(2026, 1, 1, tzinfo=UTC)
    assert attempt.failure_code == "UPLOAD_FAILED"
    assert attempt.failure_details == "Original failure details"
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_upload_attempt_update_status_applies_supplied_fields(
    session, upload_attempt_repository
):
    attempt_id = uuid4()
    attempt = MagicMock(spec=UploadAttempt)
    session.get.return_value = attempt
    completed_at = datetime.now(UTC)

    result = await upload_attempt_repository.update_status(
        attempt_id,
        UploadAttemptStatus.SUCCEEDED,
        completed_at=completed_at,
        failure_code="RETRY_RECOVERED",
        failure_details="Recovered after retry",
    )

    assert result is attempt
    assert attempt.status == UploadAttemptStatus.SUCCEEDED
    assert attempt.completed_at == completed_at
    assert attempt.failure_code == "RETRY_RECOVERED"
    assert attempt.failure_details == "Recovered after retry"
