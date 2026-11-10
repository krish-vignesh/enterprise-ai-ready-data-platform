"""Unit tests for UserRepository using a mocked AsyncSession."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.fixture
def session():
    """Provide a mocked asynchronous SQLAlchemy session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def user_repository(session):
    """Provide a UserRepository instance."""
    return UserRepository(session)


@pytest.fixture
def user():
    """Provide a User instance."""
    return User(
        keycloak_subject="keycloak-subject-123",
        email="user@example.com",
        display_name="Test User",
    )


def configure_scalar_result(session, *, one=None):
    """Configure the result returned by session.scalars()."""
    result = MagicMock()
    result.one_or_none.return_value = one
    session.scalars.return_value = result
    return result


@pytest.mark.asyncio
async def test_get_by_id_returns_user(
    session,
    user_repository,
    user,
):
    user_id = uuid4()
    session.get.return_value = user

    result = await user_repository.get_by_id(user_id)

    session.get.assert_awaited_once_with(User, user_id)
    assert result is user


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(
    session,
    user_repository,
):
    session.get.return_value = None

    result = await user_repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_keycloak_subject_returns_user(
    session,
    user_repository,
    user,
):
    configure_scalar_result(session, one=user)

    result = await user_repository.get_by_keycloak_subject(
        "keycloak-subject-123",
    )

    session.scalars.assert_awaited_once()
    assert result is user


@pytest.mark.asyncio
async def test_get_by_keycloak_subject_returns_none_when_missing(
    session,
    user_repository,
):
    configure_scalar_result(session)

    result = await user_repository.get_by_keycloak_subject(
        "unknown-subject",
    )

    assert result is None


def test_add_stages_user_without_committing(
    session,
    user_repository,
    user,
):
    result = user_repository.add(user)

    session.add.assert_called_once_with(user)
    session.commit.assert_not_called()
    assert result is user


def test_update_profile_updates_user_fields(
    session,
    user_repository,
    user,
):
    original_subject = user.keycloak_subject

    result = user_repository.update_profile(
        user,
        email="updated@example.com",
        display_name="Updated User",
    )

    assert result is user
    assert user.email == "updated@example.com"
    assert user.display_name == "Updated User"
    assert user.keycloak_subject == original_subject
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_by_id_propagates_database_error(
    session,
    user_repository,
):
    session.get.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        await user_repository.get_by_id(uuid4())


@pytest.mark.asyncio
async def test_get_by_keycloak_subject_propagates_database_error(
    session,
    user_repository,
):
    session.scalars.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        await user_repository.get_by_keycloak_subject("subject-123")
