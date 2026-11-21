"""Unit tests for DatasetRepository using a mocked AsyncSession."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dataset_repository import DatasetRepository
from app.models.dataset import Dataset


@pytest.fixture
def session():
    """Provide a mocked asynchronous database session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def repository(session):
    """Build the repository with the mocked session."""
    return DatasetRepository(session)


@pytest.mark.asyncio
async def test_get_by_id_returns_dataset(session, repository):
    dataset_id = uuid4()
    expected_dataset = MagicMock(spec=Dataset)
    session.get.return_value = expected_dataset

    result = await repository.get_by_id(dataset_id)

    session.get.assert_awaited_once_with(Dataset, dataset_id)
    assert result is expected_dataset


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(session, repository):
    session.get.return_value = None

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_source_and_name_returns_dataset(session, repository):
    source_id = uuid4()
    expected_dataset = MagicMock(spec=Dataset)

    scalar_result = MagicMock()
    scalar_result.one_or_none.return_value = expected_dataset
    session.scalars.return_value = scalar_result

    result = await repository.get_by_source_and_name(
        source_id,
        "sales",
    )

    session.scalars.assert_awaited_once()
    scalar_result.one_or_none.assert_called_once_with()
    assert result is expected_dataset


@pytest.mark.asyncio
async def test_list_by_source_returns_datasets(session, repository):
    source_id = uuid4()
    expected_datasets = [
        MagicMock(spec=Dataset),
        MagicMock(spec=Dataset),
    ]

    scalar_result = MagicMock()
    scalar_result.all.return_value = expected_datasets
    session.scalars.return_value = scalar_result

    result = await repository.list_by_source(
        source_id,
        limit=10,
        offset=5,
    )

    session.scalars.assert_awaited_once()
    assert result == expected_datasets


@pytest.mark.asyncio
async def test_list_by_source_rejects_zero_limit(repository):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await repository.list_by_source(uuid4(), limit=0)


@pytest.mark.asyncio
async def test_list_by_source_rejects_negative_offset(repository):
    with pytest.raises(ValueError, match="offset cannot be negative"):
        await repository.list_by_source(uuid4(), limit=10, offset=-1)


def test_add_stages_dataset_without_committing(session, repository):
    dataset = MagicMock(spec=Dataset)

    result = repository.add(dataset)

    session.add.assert_called_once_with(dataset)
    session.commit.assert_not_called()
    assert result is dataset

@pytest.mark.asyncio
async def test_list_by_company_with_document_counts(
    session,
    repository,
):
    company_id = uuid4()

    expected_dataset = MagicMock(spec=Dataset)

    expected_rows = [
        (expected_dataset, 10, 8),
    ]

    query_result = MagicMock()
    query_result.all.return_value = expected_rows
    session.execute.return_value = query_result

    result = await repository.list_by_company_with_document_counts(
        company_id,
        limit=10,
        offset=0,
    )

    session.execute.assert_awaited_once()

    assert result == expected_rows
    assert result[0][0] is expected_dataset
    assert result[0][1] == 10
    assert result[0][2] == 8


@pytest.mark.asyncio
async def test_list_by_company_with_document_counts_rejects_zero_limit(
    repository,
):
    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        await repository.list_by_company_with_document_counts(
            uuid4(),
            limit=0,
        )


@pytest.mark.asyncio
async def test_list_by_company_with_document_counts_rejects_negative_offset(
    repository,
):
    with pytest.raises(
        ValueError,
        match="offset cannot be negative",
    ):
        await repository.list_by_company_with_document_counts(
            uuid4(),
            limit=10,
            offset=-1,
        )
