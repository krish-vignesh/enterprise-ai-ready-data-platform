"""Unit tests for IdentityService using a mocked AsyncSession."""

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.identity_service import (
    IdentityService,
    USER_SUBJECT_UNIQUE_CONSTRAINT,
)


# ---------------------------------------------------------------------
# Fixtures and test helpers
# ---------------------------------------------------------------------


@pytest.fixture
def session():
    """Provide a mocked asynchronous SQLAlchemy session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def user():
    """Provide an existing internal User."""
    return User(
        keycloak_subject="keycloak-subject-123",
        email="user@example.com",
        display_name="Test User",
    )


@pytest.fixture
def repository():
    """Provide a mocked UserRepository."""
    repo = MagicMock()
    repo.get_by_keycloak_subject = AsyncMock()
    return repo


def create_transaction():
    """Create a mocked asynchronous transaction context manager."""
    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=None)
    transaction.__aexit__ = AsyncMock(return_value=False)
    return transaction


def create_integrity_error(constraint_name):
    """Create an IntegrityError exposing a PostgreSQL constraint name."""
    original_error = SimpleNamespace(
        diag=SimpleNamespace(constraint_name=constraint_name)
    )

    return IntegrityError(
        "INSERT INTO users",
        {},
        original_error,
    )


# ---------------------------------------------------------------------
# Test 1 — New user provisioning
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_creates_new_user(
    session,
    repository,
):
    transaction = create_transaction()
    session.begin.return_value = transaction
    repository.get_by_keycloak_subject.return_value = None

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject="keycloak-subject-123",
            email="user@example.com",
            display_name="Test User",
        )

    repository.get_by_keycloak_subject.assert_awaited_once_with("keycloak-subject-123")

    repository.add.assert_called_once()

    created_user = repository.add.call_args.args[0]

    assert isinstance(created_user, User)
    assert created_user.keycloak_subject == "keycloak-subject-123"
    assert created_user.email == "user@example.com"
    assert created_user.display_name == "Test User"

    session.flush.assert_awaited_once()
    assert result is created_user

    transaction.__aenter__.assert_awaited_once()
    transaction.__aexit__.assert_awaited_once()


# ---------------------------------------------------------------------
# Test 2 — Existing user resolution
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_returns_existing_user(
    session,
    repository,
    user,
):
    session.begin.return_value = create_transaction()
    repository.get_by_keycloak_subject.return_value = user

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject=user.keycloak_subject,
            email=user.email,
            display_name=user.display_name,
        )

    assert result is user
    repository.add.assert_not_called()
    session.flush.assert_not_awaited()
    repository.update_profile.assert_not_called()


# ---------------------------------------------------------------------
# Test 3 — Email synchronization
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_updates_email(
    session,
    repository,
    user,
):
    session.begin.return_value = create_transaction()
    repository.get_by_keycloak_subject.return_value = user

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject=user.keycloak_subject,
            email="updated@example.com",
            display_name=user.display_name,
        )

    assert result is user
    repository.update_profile.assert_called_once_with(
        user,
        email="updated@example.com",
        display_name="Test User",
    )

    repository.update_profile.assert_called_once_with(
        user,
        email="updated@example.com",
        display_name="Test User",
    )


# ---------------------------------------------------------------------
# Test 4 — Display-name synchronization
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_updates_display_name(
    session,
    repository,
    user,
):
    session.begin.return_value = create_transaction()
    repository.get_by_keycloak_subject.return_value = user

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject=user.keycloak_subject,
            email=user.email,
            display_name="Updated User",
        )

    assert result is user
    repository.update_profile.assert_called_once_with(
        user,
        email="user@example.com",
        display_name="Updated User",
    )

    repository.update_profile.assert_called_once_with(
        user,
        email="user@example.com",
        display_name="Updated User",
    )


# ---------------------------------------------------------------------
# Test 5 — Missing optional claims
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_preserves_missing_claims(
    session,
    repository,
    user,
):
    session.begin.return_value = create_transaction()
    repository.get_by_keycloak_subject.return_value = user

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject=user.keycloak_subject,
            email=None,
            display_name=None,
        )

    assert result is user
    assert user.email == "user@example.com"
    assert user.display_name == "Test User"

    repository.update_profile.assert_not_called()


# ---------------------------------------------------------------------
# Test 6 — Successful transaction commit
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_commits_successfully(
    session,
    repository,
):
    transaction = create_transaction()
    session.begin.return_value = transaction
    repository.get_by_keycloak_subject.return_value = None

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        await service.resolve_or_provision_user(
            keycloak_subject="keycloak-subject-123",
            email="user@example.com",
            display_name="Test User",
        )

    transaction.__aexit__.assert_awaited_once_with(
        None,
        None,
        None,
    )


# ---------------------------------------------------------------------
# Test 7 — Transaction rollback on failure
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_rolls_back_on_failure(
    session,
    repository,
):
    transaction = create_transaction()
    session.begin.return_value = transaction

    repository.get_by_keycloak_subject.side_effect = RuntimeError(
        "Database unavailable"
    )

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        with pytest.raises(RuntimeError, match="Database unavailable"):
            await service.resolve_or_provision_user(
                keycloak_subject="keycloak-subject-123",
                email="user@example.com",
                display_name="Test User",
            )

    transaction.__aexit__.assert_awaited_once()

    exit_arguments = transaction.__aexit__.await_args.args

    assert exit_arguments[0] is RuntimeError


# ---------------------------------------------------------------------
# Test 8 — Concurrent duplicate-subject recovery
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_recovers_duplicate_subject(
    session,
    repository,
    user,
):
    failed_transaction = create_transaction()
    recovery_transaction = create_transaction()

    session.begin.side_effect = [
        failed_transaction,
        recovery_transaction,
    ]

    repository.get_by_keycloak_subject.side_effect = [
        None,
        user,
    ]

    session.flush.side_effect = create_integrity_error(USER_SUBJECT_UNIQUE_CONSTRAINT)

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject=user.keycloak_subject,
            email=user.email,
            display_name=user.display_name,
        )

    assert result is user

    assert repository.get_by_keycloak_subject.await_count == 2
    repository.add.assert_called_once()

    assert session.begin.call_count == 2

    failed_transaction.__aexit__.assert_awaited_once()
    recovery_transaction.__aexit__.assert_awaited_once_with(
        None,
        None,
        None,
    )


# ---------------------------------------------------------------------
# Test 9 — Unrelated IntegrityError propagation
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_propagates_unrelated_integrity_error(
    session,
    repository,
):
    transaction = create_transaction()
    session.begin.return_value = transaction

    unrelated_error = create_integrity_error("some_other_constraint")

    repository.get_by_keycloak_subject.return_value = None
    session.flush.side_effect = unrelated_error

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        with pytest.raises(IntegrityError) as exc_info:
            await service.resolve_or_provision_user(
                keycloak_subject="keycloak-subject-123",
                email="user@example.com",
                display_name="Test User",
            )

    assert exc_info.value is unrelated_error
    assert session.begin.call_count == 1


# ---------------------------------------------------------------------
# Test 10 — Winning user unavailable during recovery
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_propagates_error_when_winner_missing(
    session,
    repository,
):
    failed_transaction = create_transaction()
    recovery_transaction = create_transaction()

    session.begin.side_effect = [
        failed_transaction,
        recovery_transaction,
    ]

    repository.get_by_keycloak_subject.side_effect = [
        None,
        None,
    ]

    duplicate_error = create_integrity_error(USER_SUBJECT_UNIQUE_CONSTRAINT)

    session.flush.side_effect = duplicate_error

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        with pytest.raises(IntegrityError) as exc_info:
            await service.resolve_or_provision_user(
                keycloak_subject="keycloak-subject-123",
                email="user@example.com",
                display_name="Test User",
            )

    assert exc_info.value is duplicate_error
    assert session.begin.call_count == 2


# ---------------------------------------------------------------------
# Test 11 — Profile synchronization during recovery
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_syncs_profile_during_recovery(
    session,
    repository,
    user,
):
    failed_transaction = create_transaction()
    recovery_transaction = create_transaction()

    session.begin.side_effect = [
        failed_transaction,
        recovery_transaction,
    ]

    repository.get_by_keycloak_subject.side_effect = [
        None,
        user,
    ]

    session.flush.side_effect = create_integrity_error(USER_SUBJECT_UNIQUE_CONSTRAINT)

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        result = await service.resolve_or_provision_user(
            keycloak_subject=user.keycloak_subject,
            email="latest@example.com",
            display_name="Latest User",
        )

    assert result is user

    repository.update_profile.assert_called_once_with(
        user,
        email="latest@example.com",
        display_name="Latest User",
    )


# ---------------------------------------------------------------------
# Test 12 — Database error propagation
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_propagates_database_error(
    session,
    repository,
):
    transaction = create_transaction()
    session.begin.return_value = transaction

    repository.get_by_keycloak_subject.side_effect = RuntimeError(
        "PostgreSQL connection lost"
    )

    with patch(
        "app.services.identity_service.UserRepository",
        return_value=repository,
    ):
        service = IdentityService(session)

        with pytest.raises(
            RuntimeError,
            match="PostgreSQL connection lost",
        ):
            await service.resolve_or_provision_user(
                keycloak_subject="keycloak-subject-123",
                email="user@example.com",
                display_name="Test User",
            )

    transaction.__aexit__.assert_awaited_once()


# ---------------------------------------------------------------------
# Test 13 — Business event logging
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_or_provision_user_logs_successful_provisioning(
    session,
    repository,
    caplog,
):
    session.begin.return_value = create_transaction()
    repository.get_by_keycloak_subject.return_value = None

    with (
        patch(
            "app.services.identity_service.UserRepository",
            return_value=repository,
        ),
        caplog.at_level(
            logging.INFO,
            logger="app.services.identity_service",
        ),
    ):
        service = IdentityService(session)

        await service.resolve_or_provision_user(
            keycloak_subject="keycloak-subject-123",
            email="user@example.com",
            display_name="Test User",
        )

    assert "identity.user.provisioned" in caplog.text
