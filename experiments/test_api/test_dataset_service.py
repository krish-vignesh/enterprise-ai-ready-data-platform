
"""Unit tests for DatasetService using mocked dependencies."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.dataset_service as service_module
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetListItemResponse, DatasetResponse
from app.schemas.document_upload import DocumentResponse
from app.services.dataset_service import (
    DATASET_NAME_UNIQUE_CONSTRAINT,
    DatasetAlreadyExistsError,
    DatasetService,
)


# ---------------------------------------------------------------------
# Fixtures and test helpers
# ---------------------------------------------------------------------


@pytest.fixture
def session():
    """Provide a mocked asynchronous SQLAlchemy session."""

    mocked_session = MagicMock(spec=AsyncSession)
    mocked_session.flush = AsyncMock()
    mocked_session.commit = AsyncMock()
    mocked_session.rollback = AsyncMock()

    return mocked_session


@pytest.fixture
def dataset_repository():
    """Provide a mocked DatasetRepository."""

    repository = MagicMock()
    repository.get_by_source_and_name = AsyncMock()
    repository.list_by_company_with_document_counts = AsyncMock()
    repository.add = MagicMock()

    return repository


@pytest.fixture
def document_repository():
    """Provide a mocked DocumentRepository."""

    repository = MagicMock()
    repository.list_by_dataset = AsyncMock()

    return repository


@pytest.fixture
def service(
    monkeypatch,
    session,
    dataset_repository,
    document_repository,
):
    """Build DatasetService with mocked repository dependencies."""

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

    return DatasetService(session)


# ---------------------------------------------------------------------
# Dataset creation tests
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_dataset_successfully(
    service,
    session,
    dataset_repository,
):
    source_id = uuid4()
    dataset_id = uuid4()

    dataset_repository.get_by_source_and_name.return_value = None

    async def assign_dataset_id():
        dataset = dataset_repository.add.call_args.args[0]
        dataset.dataset_id = dataset_id

    session.flush.side_effect = assign_dataset_id

    result = await service.create_dataset(
        source_id=source_id,
        dataset_name="Sales Data",
    )

    dataset_repository.get_by_source_and_name.assert_awaited_once_with(
        source_id,
        "Sales Data",
    )

    dataset_repository.add.assert_called_once()

    created_dataset = dataset_repository.add.call_args.args[0]

    assert isinstance(created_dataset, Dataset)
    assert created_dataset.dataset_id == dataset_id
    assert created_dataset.source_id == source_id
    assert created_dataset.dataset_name == "Sales Data"

    assert result is created_dataset

    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_dataset_rejects_existing_name(
    service,
    session,
    dataset_repository,
):
    source_id = uuid4()

    dataset_repository.get_by_source_and_name.return_value = (
        MagicMock(spec=Dataset)
    )

    with pytest.raises(
        DatasetAlreadyExistsError,
        match="already exists",
    ):
        await service.create_dataset(
            source_id=source_id,
            dataset_name="Sales Data",
        )

    dataset_repository.add.assert_not_called()

    session.flush.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_dataset_handles_concurrent_duplicate(
    service,
    session,
    dataset_repository,
):
    source_id = uuid4()

    dataset_repository.get_by_source_and_name.return_value = None

    diagnostic = MagicMock()
    diagnostic.constraint_name = DATASET_NAME_UNIQUE_CONSTRAINT

    original_error = MagicMock()
    original_error.diag = diagnostic

    integrity_error = IntegrityError(
        "INSERT INTO datasets",
        {},
        original_error,
    )

    session.flush.side_effect = integrity_error

    with pytest.raises(
        DatasetAlreadyExistsError,
        match="already exists",
    ):
        await service.create_dataset(
            source_id=source_id,
            dataset_name="Sales Data",
        )

    dataset_repository.add.assert_called_once()

    session.flush.assert_awaited_once()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_dataset_rolls_back_on_unexpected_failure(
    service,
    session,
    dataset_repository,
):
    dataset_repository.get_by_source_and_name.return_value = None

    session.flush.side_effect = RuntimeError(
        "Database insertion failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Database insertion failed",
    ):
        await service.create_dataset(
            source_id=uuid4(),
            dataset_name="Sales Data",
        )

    dataset_repository.add.assert_called_once()

    session.flush.assert_awaited_once()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()





# ---------------------------------------------------------------------
# Company Dataset listing tests
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_company_datasets_maps_repository_results(
    service,
    dataset_repository,
):
    company_id = uuid4()
    dataset_id = uuid4()
    source_id = uuid4()

    dataset = SimpleNamespace(
        dataset_id=dataset_id,
        source_id=source_id,
        dataset_name="Sales Data",
    )

    dataset_repository.list_by_company_with_document_counts.return_value = [
        (dataset, 10, 8),
    ]

    result = await service.list_company_datasets(
        company_id,
        limit=20,
        offset=5,
    )

    dataset_repository.list_by_company_with_document_counts.assert_awaited_once_with(
        company_id,
        limit=20,
        offset=5,
    )

    assert len(result) == 1
    assert isinstance(result[0], DatasetListItemResponse)
    assert result[0].dataset_id == dataset_id
    assert result[0].source_id == source_id
    assert result[0].dataset_name == "Sales Data"
    assert result[0].document_count == 10
    assert result[0].available_document_count == 8


@pytest.mark.asyncio
async def test_list_company_datasets_returns_empty_list(
    service,
    dataset_repository,
):
    dataset_repository.list_by_company_with_document_counts.return_value = []

    result = await service.list_company_datasets(
        uuid4(),
        limit=20,
    )

    assert result == []

    dataset_repository.list_by_company_with_document_counts.assert_awaited_once_with(
        dataset_repository.list_by_company_with_document_counts.call_args.args[0],
        limit=20,
        offset=0,
    )


# ---------------------------------------------------------------------
# Dataset metadata retrieval tests
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_dataset_returns_dataset_response(service):
    dataset_id = uuid4()
    source_id = uuid4()

    dataset = SimpleNamespace(
        dataset_id=dataset_id,
        source_id=source_id,
        dataset_name="Sales Data",
    )

    result = await service.get_dataset(dataset)

    assert isinstance(result, DatasetResponse)
    assert result.dataset_id == dataset_id
    assert result.source_id == source_id
    assert result.dataset_name == "Sales Data"


# ---------------------------------------------------------------------
# Dataset document listing tests
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_dataset_documents_maps_repository_results(
    service,
    document_repository,
):
    dataset_id = uuid4()
    document_id = uuid4()

    dataset = SimpleNamespace(dataset_id=dataset_id)

    document = SimpleNamespace(
        document_id=document_id,
        dataset_id=dataset_id,
        original_filename="sales.csv",
        detected_format="csv",
        content_type="text/csv",
        file_size_bytes=1024,
        sha256="a" * 64,
        status="AVAILABLE",
    )

    document_repository.list_by_dataset.return_value = [document]

    result = await service.list_dataset_documents(
        dataset,
        limit=10,
        offset=5,
    )

    document_repository.list_by_dataset.assert_awaited_once_with(
        dataset_id,
        limit=10,
        offset=5,
    )

    assert len(result) == 1
    assert isinstance(result[0], DocumentResponse)
    assert result[0].document_id == document_id
    assert result[0].dataset_id == dataset_id
    assert result[0].original_filename == "sales.csv"
    assert result[0].detected_format == "csv"
    assert result[0].file_size_bytes == 1024
    assert result[0].status.value == "AVAILABLE"


@pytest.mark.asyncio
async def test_list_dataset_documents_returns_empty_list(
    service,
    document_repository,
):
    dataset = SimpleNamespace(dataset_id=uuid4())

    document_repository.list_by_dataset.return_value = []

    result = await service.list_dataset_documents(
        dataset,
        limit=10,
    )

    assert result == []

    document_repository.list_by_dataset.assert_awaited_once_with(
        dataset.dataset_id,
        limit=10,
        offset=0,
    )
