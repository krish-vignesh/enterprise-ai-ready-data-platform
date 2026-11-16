"""Unit tests for SourceSystemService using mocked dependencies."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.source_system_service as service_module
from app.models.source_system import SourceSystem
from app.services.source_system_service import SourceSystemService


# ---------------------------------------------------------------------
# Fixtures and test helpers
# ---------------------------------------------------------------------


@pytest.fixture
def transaction():
    """Provide a mocked asynchronous transaction context manager."""

    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=None)
    transaction.__aexit__ = AsyncMock(return_value=False)

    return transaction


@pytest.fixture
def session(transaction):
    """Provide a mocked asynchronous SQLAlchemy session."""

    session = MagicMock(spec=AsyncSession)
    session.begin.return_value = transaction
    session.flush = AsyncMock()

    return session


@pytest.fixture
def source_repository():
    """Provide a mocked SourceSystemRepository."""

    repository = MagicMock()
    repository.get_by_id = AsyncMock()
    repository.list_by_company = AsyncMock()

    return repository


@pytest.fixture
def service(monkeypatch, session, source_repository):
    """Build SourceSystemService with a mocked repository."""

    monkeypatch.setattr(
        service_module,
        "SourceSystemRepository",
        lambda _session: source_repository,
    )

    return SourceSystemService(session)


# ---------------------------------------------------------------------
# Test 1 — Successful source-system creation
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_source_system_successfully(
    service,
    session,
    transaction,
    source_repository,
):
    source_id = uuid4()

    async def assign_source_id():
        source = source_repository.add.call_args.args[0]
        source.source_id = source_id

    session.flush.side_effect = assign_source_id

    company_id = uuid4()

    result = await service.create_source_system(
        company_id=company_id,
        source_name="Salesforce",
        source_type="CRM",
    )

    source_repository.add.assert_called_once()

    created_source = source_repository.add.call_args.args[0]

    assert isinstance(created_source, SourceSystem)
    assert created_source.source_id == source_id
    assert created_source.company_id == company_id
    assert created_source.source_name == "Salesforce"
    assert created_source.source_type == "CRM"

    assert result is created_source

    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


# ---------------------------------------------------------------------
# Test 2 — Transaction rollback when creation fails
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_source_system_rolls_back_on_failure(
    service,
    session,
    transaction,
    source_repository,
):
    session.flush.side_effect = RuntimeError("Source system insertion failed")

    with pytest.raises(
        RuntimeError,
        match="Source system insertion failed",
    ):
        await service.create_source_system(
            company_id=uuid4(),
            source_name="Salesforce",
            source_type="CRM",
        )

    source_repository.add.assert_called_once()

    session.flush.assert_awaited_once()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


# ---------------------------------------------------------------------
# Test 3 — List source systems for a company
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_source_systems_delegates_to_repository(
    service,
    source_repository,
):
    company_id = uuid4()

    expected_sources = [
        MagicMock(spec=SourceSystem),
        MagicMock(spec=SourceSystem),
    ]

    source_repository.list_by_company.return_value = expected_sources

    result = await service.list_source_systems(
        company_id,
        limit=10,
        offset=5,
    )

    source_repository.list_by_company.assert_awaited_once_with(
        company_id,
        limit=10,
        offset=5,
    )

    assert result == expected_sources


# ---------------------------------------------------------------------
# Test 4 — List source systems with default offset
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_source_systems_uses_default_offset(
    service,
    source_repository,
):
    company_id = uuid4()

    source_repository.list_by_company.return_value = []

    result = await service.list_source_systems(
        company_id,
        limit=20,
    )

    source_repository.list_by_company.assert_awaited_once_with(
        company_id,
        limit=20,
        offset=0,
    )

    assert result == []


# ---------------------------------------------------------------------
# Test 5 — Retrieve an existing source system
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_source_system_returns_existing_source(
    service,
    source_repository,
):
    source_id = uuid4()
    expected_source = MagicMock(spec=SourceSystem)

    source_repository.get_by_id.return_value = expected_source

    result = await service.get_source_system(source_id)

    source_repository.get_by_id.assert_awaited_once_with(source_id)

    assert result is expected_source


# ---------------------------------------------------------------------
# Test 6 — Return None when source system does not exist
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_source_system_returns_none_when_missing(
    service,
    source_repository,
):
    source_repository.get_by_id.return_value = None

    result = await service.get_source_system(uuid4())

    assert result is None
    source_repository.get_by_id.assert_awaited_once()


# ---------------------------------------------------------------------
# Test 7 — Propagate listing database errors
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_source_systems_propagates_database_error(
    service,
    source_repository,
):
    source_repository.list_by_company.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(
        RuntimeError,
        match="Database unavailable",
    ):
        await service.list_source_systems(
            uuid4(),
            limit=10,
        )


# ---------------------------------------------------------------------
# Test 8 — Propagate retrieval database errors
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_source_system_propagates_database_error(
    service,
    source_repository,
):
    source_repository.get_by_id.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(
        RuntimeError,
        match="Database unavailable",
    ):
        await service.get_source_system(uuid4())
