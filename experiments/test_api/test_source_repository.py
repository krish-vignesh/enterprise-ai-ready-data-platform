"""Unit tests for SourceSystemRepository using a mocked AsyncSession."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source_system import SourceSystem
from app.repositories.source_repository import SourceSystemRepository


@pytest.fixture
def session():
    """Provide a mocked asynchronous database session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def repository(session):
    """Build the repository with the mocked session."""
    return SourceSystemRepository(session)


@pytest.mark.asyncio
async def test_get_by_id_returns_source(session, repository):
    source_id = uuid4()
    expected_source = MagicMock(spec=SourceSystem)
    session.get.return_value = expected_source

    result = await repository.get_by_id(source_id)

    session.get.assert_awaited_once_with(SourceSystem, source_id)
    assert result is expected_source


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(session, repository):
    session.get.return_value = None

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_list_by_company_returns_sources(session, repository):
    company_id = uuid4()
    expected_sources = [
        MagicMock(spec=SourceSystem),
        MagicMock(spec=SourceSystem),
    ]

    scalar_result = MagicMock()
    scalar_result.all.return_value = expected_sources
    session.scalars.return_value = scalar_result

    result = await repository.list_by_company(
        company_id,
        limit=10,
        offset=5,
    )

    session.scalars.assert_awaited_once()
    assert result == expected_sources


@pytest.mark.asyncio
async def test_list_by_company_rejects_zero_limit(repository):
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        await repository.list_by_company(uuid4(), limit=0)


@pytest.mark.asyncio
async def test_list_by_company_rejects_negative_offset(repository):
    with pytest.raises(ValueError, match="offset cannot be negative"):
        await repository.list_by_company(uuid4(), limit=10, offset=-1)


def test_add_stages_source_without_committing(session, repository):
    source = MagicMock(spec=SourceSystem)

    result = repository.add(source)

    session.add.assert_called_once_with(source)
    session.commit.assert_not_called()
    assert result is source
