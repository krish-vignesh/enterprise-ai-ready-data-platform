"""Tests for the current-user FastAPI dependency."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.authentication import get_token_claims
from app.core.security.current_user import get_current_user
from app.db.dependencies import get_db
from app.models.user import User


def create_test_app(
    token_claims: dict,
    session: AsyncSession,
) -> FastAPI:
    """Create a test application with overridden request dependencies."""

    app = FastAPI()

    async def override_token_claims() -> dict:
        return token_claims

    async def override_db():
        yield session

    app.dependency_overrides[get_token_claims] = override_token_claims
    app.dependency_overrides[get_db] = override_db

    @app.get("/current-user")
    async def current_user_endpoint(
        current_user: User = Depends(get_current_user),
    ) -> dict:
        return {
            "keycloak_subject": current_user.keycloak_subject,
            "email": current_user.email,
            "display_name": current_user.display_name,
        }

    return app


def create_mock_identity_service() -> MagicMock:
    """Create a mocked IdentityService."""

    identity_service = MagicMock()
    identity_service.resolve_or_provision_user = AsyncMock()

    return identity_service


def test_get_current_user_resolves_user_from_validated_claims() -> None:
    """Validated identity claims must be passed to IdentityService."""

    token_claims = {
        "sub": "keycloak-subject-123",
        "email": "user@example.com",
        "name": "Test User",
    }

    session = MagicMock(spec=AsyncSession)

    expected_user = User(
        keycloak_subject="keycloak-subject-123",
        email="user@example.com",
        display_name="Test User",
    )

    identity_service = create_mock_identity_service()
    identity_service.resolve_or_provision_user.return_value = expected_user

    app = create_test_app(token_claims, session)

    with (
        patch(
            "app.core.security.current_user.IdentityService",
            return_value=identity_service,
        ) as identity_service_class,
        TestClient(app) as client,
    ):
        response = client.get("/current-user")

    assert response.status_code == 200
    assert response.json() == {
        "keycloak_subject": "keycloak-subject-123",
        "email": "user@example.com",
        "display_name": "Test User",
    }

    identity_service_class.assert_called_once_with(session)

    identity_service.resolve_or_provision_user.assert_awaited_once_with(
        keycloak_subject="keycloak-subject-123",
        email="user@example.com",
        display_name="Test User",
    )


def test_get_current_user_handles_missing_optional_claims() -> None:
    """Missing email and name claims must be passed as None."""

    token_claims = {
        "sub": "keycloak-subject-123",
    }

    session = MagicMock(spec=AsyncSession)

    expected_user = User(
        keycloak_subject="keycloak-subject-123",
    )

    identity_service = create_mock_identity_service()
    identity_service.resolve_or_provision_user.return_value = expected_user

    app = create_test_app(token_claims, session)

    with (
        patch(
            "app.core.security.current_user.IdentityService",
            return_value=identity_service,
        ),
        TestClient(app) as client,
    ):
        response = client.get("/current-user")

    assert response.status_code == 200
    assert response.json() == {
        "keycloak_subject": "keycloak-subject-123",
        "email": None,
        "display_name": None,
    }

    identity_service.resolve_or_provision_user.assert_awaited_once_with(
        keycloak_subject="keycloak-subject-123",
        email=None,
        display_name=None,
    )


def test_get_current_user_ignores_invalid_optional_claim_types() -> None:
    """Non-string optional claims must be normalized to None."""

    token_claims = {
        "sub": "keycloak-subject-123",
        "email": 12345,
        "name": ["Unexpected", "Value"],
    }

    session = MagicMock(spec=AsyncSession)

    expected_user = User(
        keycloak_subject="keycloak-subject-123",
    )

    identity_service = create_mock_identity_service()
    identity_service.resolve_or_provision_user.return_value = expected_user

    app = create_test_app(token_claims, session)

    with (
        patch(
            "app.core.security.current_user.IdentityService",
            return_value=identity_service,
        ),
        TestClient(app) as client,
    ):
        response = client.get("/current-user")

    assert response.status_code == 200

    identity_service.resolve_or_provision_user.assert_awaited_once_with(
        keycloak_subject="keycloak-subject-123",
        email=None,
        display_name=None,
    )


def test_get_current_user_ignores_blank_optional_claims() -> None:
    """Whitespace-only optional claims must be normalized to None."""

    token_claims = {
        "sub": "keycloak-subject-123",
        "email": "   ",
        "name": "   ",
    }

    session = MagicMock(spec=AsyncSession)

    expected_user = User(
        keycloak_subject="keycloak-subject-123",
    )

    identity_service = create_mock_identity_service()
    identity_service.resolve_or_provision_user.return_value = expected_user

    app = create_test_app(token_claims, session)

    with (
        patch(
            "app.core.security.current_user.IdentityService",
            return_value=identity_service,
        ),
        TestClient(app) as client,
    ):
        response = client.get("/current-user")

    assert response.status_code == 200

    identity_service.resolve_or_provision_user.assert_awaited_once_with(
        keycloak_subject="keycloak-subject-123",
        email=None,
        display_name=None,
    )
