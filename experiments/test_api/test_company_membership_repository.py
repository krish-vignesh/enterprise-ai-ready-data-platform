"""Unit tests for CompanyMembershipRepository using a mocked AsyncSession."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_membership import CompanyMembership, CompanyRole
from app.repositories.company_membership_repository import (
    CompanyMembershipRepository,
)


@pytest.fixture
def session():
    """Provide a mocked asynchronous SQLAlchemy session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def membership_repository(session):
    """Provide a CompanyMembershipRepository instance."""
    return CompanyMembershipRepository(session)


@pytest.fixture
def membership():
    """Provide a company membership instance."""
    return CompanyMembership(
        user_id=uuid4(),
        company_id=uuid4(),
        role=CompanyRole.MEMBER,
    )


def configure_scalar_result(session, *, one=None, all=None):
    """Configure the result returned by session.scalars()."""
    result = MagicMock()
    result.one_or_none.return_value = one
    result.all.return_value = [] if all is None else all
    session.scalars.return_value = result
    return result


@pytest.mark.asyncio
async def test_get_by_id_returns_membership(
    session,
    membership_repository,
    membership,
):
    membership_id = uuid4()
    session.get.return_value = membership

    result = await membership_repository.get_by_id(membership_id)

    session.get.assert_awaited_once_with(
        CompanyMembership,
        membership_id,
    )
    assert result is membership


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(
    session,
    membership_repository,
):
    session.get.return_value = None

    result = await membership_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_user_and_company_returns_membership(
    session,
    membership_repository,
    membership,
):
    configure_scalar_result(session, one=membership)

    result = await membership_repository.get_by_user_and_company(
        membership.user_id,
        membership.company_id,
    )

    session.scalars.assert_awaited_once()
    assert result is membership


@pytest.mark.asyncio
async def test_get_by_user_and_company_returns_none_when_missing(
    session,
    membership_repository,
):
    configure_scalar_result(session)

    result = await membership_repository.get_by_user_and_company(
        uuid4(),
        uuid4(),
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_by_user_id_returns_all_memberships(
    session,
    membership_repository,
):
    expected = [
        MagicMock(spec=CompanyMembership),
        MagicMock(spec=CompanyMembership),
    ]
    configure_scalar_result(session, all=expected)
    user_id = uuid4()

    result = await membership_repository.get_by_user_id(user_id)

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_get_by_user_id_returns_empty_list_when_missing(
    session,
    membership_repository,
):
    configure_scalar_result(session)

    result = await membership_repository.get_by_user_id(uuid4())

    assert result == []


@pytest.mark.asyncio
async def test_get_by_company_id_returns_all_memberships(
    session,
    membership_repository,
):
    expected = [
        MagicMock(spec=CompanyMembership),
        MagicMock(spec=CompanyMembership),
    ]
    configure_scalar_result(session, all=expected)
    company_id = uuid4()

    result = await membership_repository.get_by_company_id(company_id)

    session.scalars.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_get_by_company_id_returns_empty_list_when_missing(
    session,
    membership_repository,
):
    configure_scalar_result(session)

    result = await membership_repository.get_by_company_id(uuid4())

    assert result == []


def test_add_stages_membership_without_committing(
    session,
    membership_repository,
    membership,
):
    result = membership_repository.add(membership)

    session.add.assert_called_once_with(membership)
    session.commit.assert_not_called()
    assert result is membership


def test_update_role_changes_membership_role(
    session,
    membership_repository,
    membership,
):
    result = membership_repository.update_role(
        membership,
        role=CompanyRole.ADMIN,
    )

    assert result is membership
    assert membership.role == CompanyRole.ADMIN
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_stages_membership_without_committing(
    session,
    membership_repository,
    membership,
):
    await membership_repository.delete(membership)

    session.delete.assert_awaited_once_with(membership)
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_by_id_propagates_database_error(
    session,
    membership_repository,
):
    session.get.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        await membership_repository.get_by_id(uuid4())


@pytest.mark.asyncio
async def test_get_by_user_and_company_propagates_database_error(
    session,
    membership_repository,
):
    session.scalars.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        await membership_repository.get_by_user_and_company(
            uuid4(),
            uuid4(),
        )


@pytest.mark.asyncio
async def test_delete_propagates_database_error(
    session,
    membership_repository,
    membership,
):
    session.delete.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        await membership_repository.delete(membership)
