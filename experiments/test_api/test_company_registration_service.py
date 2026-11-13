
"""Unit tests for CompanyRegistrationService using a mocked AsyncSession."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.company_registration_service as service_module
from app.models.company import Company
from app.models.company_membership import CompanyMembership, CompanyRole
from app.services.company_registration_service import (
    CompanyRegistrationService,
)


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
def company_repository():
    """Provide a mocked CompanyRepository."""
    return MagicMock()


@pytest.fixture
def membership_repository():
    """Provide a mocked CompanyMembershipRepository."""
    return MagicMock()


@pytest.fixture
def service(
    monkeypatch,
    session,
    company_repository,
    membership_repository,
):
    """Provide a CompanyRegistrationService with mocked repositories."""

    monkeypatch.setattr(
        service_module,
        "CompanyRepository",
        lambda _session: company_repository,
    )

    monkeypatch.setattr(
        service_module,
        "CompanyMembershipRepository",
        lambda _session: membership_repository,
    )

    return CompanyRegistrationService(session)


def assign_company_id_on_flush(company_repository):
    """Simulate SQLAlchemy assigning a generated company UUID during flush."""

    async def flush():
        company = company_repository.add.call_args.args[0]

        if company.company_id is None:
            company.company_id = uuid4()

    return flush


# ---------------------------------------------------------------------
# Test 1 — Successful company registration
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_company_creates_company_and_owner_membership(
    service,
    session,
    transaction,
    company_repository,
    membership_repository,
):
    session.flush.side_effect = assign_company_id_on_flush(
        company_repository
    )

    user_id = uuid4()

    result = await service.register_company(
        company_name="ABC Technologies",
        user_id=user_id,
    )

    company_repository.add.assert_called_once()

    created_company = company_repository.add.call_args.args[0]

    assert isinstance(created_company, Company)
    assert created_company.company_name == "ABC Technologies"
    assert created_company.company_id is not None

    membership_repository.add.assert_called_once()

    created_membership = membership_repository.add.call_args.args[0]

    assert isinstance(created_membership, CompanyMembership)
    assert created_membership.company_id == created_company.company_id
    assert created_membership.user_id == user_id
    assert created_membership.role == CompanyRole.OWNER

    assert result is created_company

    assert session.flush.await_count == 2
    session.commit.assert_not_called()

    transaction.__aexit__.assert_awaited_once_with(
        None,
        None,
        None,
    )


# ---------------------------------------------------------------------
# Test 2 — Rollback when membership insertion fails
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_company_rolls_back_when_membership_flush_fails(
    service,
    session,
    transaction,
    company_repository,
    membership_repository,
):
    async def flush_then_fail():
        company = company_repository.add.call_args.args[0]

        if company.company_id is None:
            company.company_id = uuid4()
            return

        raise RuntimeError("Membership insertion failed")

    session.flush.side_effect = flush_then_fail

    with pytest.raises(
        RuntimeError,
        match="Membership insertion failed",
    ):
        await service.register_company(
            company_name="ABC Technologies",
            user_id=uuid4(),
        )

    company_repository.add.assert_called_once()
    membership_repository.add.assert_called_once()

    assert session.flush.await_count == 2

    transaction.__aexit__.assert_awaited_once()

    exit_arguments = transaction.__aexit__.await_args.args

    assert exit_arguments[0] is RuntimeError
    assert isinstance(exit_arguments[1], RuntimeError)

    session.commit.assert_not_called()
