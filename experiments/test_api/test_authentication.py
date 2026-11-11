"""Tests for FastAPI request-level authentication."""

from typing import Annotated, Any
from unittest.mock import AsyncMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.security.authentication import get_token_claims
from app.core.security.jwt_validator import (
    JWKSUnavailableError,
    JWTValidationError,
    JWTValidator,
)


def create_test_app(
    jwt_validator: AsyncMock | None = None,
) -> FastAPI:
    """Create a small FastAPI application for authentication tests."""

    app = FastAPI()

    if jwt_validator is not None:
        app.state.jwt_validator = jwt_validator

    @app.get("/protected")
    async def protected_endpoint(
        claims: Annotated[
            dict[str, Any],
            Depends(get_token_claims),
        ],
    ) -> dict[str, Any]:
        return {"claims": claims}

    return app


def create_mock_validator() -> AsyncMock:
    """Create a mock JWTValidator without contacting Keycloak."""

    return AsyncMock(spec=JWTValidator)


def test_missing_bearer_token_returns_401() -> None:
    """A request without an Authorization header must be rejected."""

    validator = create_mock_validator()
    client = TestClient(create_test_app(validator))

    response = client.get("/protected")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    validator.validate_token.assert_not_awaited()


@pytest.mark.parametrize(
    "authorization_header",
    [
        "Bearer",
        "Bearer ",
        "Basic abc123",
    ],
)
def test_invalid_authorization_header_returns_401(
    authorization_header: str,
) -> None:
    """Empty or unsupported authorization credentials must be rejected."""

    validator = create_mock_validator()
    client = TestClient(create_test_app(validator))

    response = client.get(
        "/protected",
        headers={"Authorization": authorization_header},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    validator.validate_token.assert_not_awaited()


def test_valid_token_returns_validated_claims() -> None:
    """A valid token must return the claims produced by JWTValidator."""

    validator = create_mock_validator()

    expected_claims = {
        "sub": "keycloak-user-123",
        "iss": "http://localhost:8081/realms/enterprise-platform",
        "aud": ["enterprise-platform-api", "account"],
        "email": "user@example.com",
    }

    validator.validate_token.return_value = expected_claims

    client = TestClient(create_test_app(validator))

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer valid-test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"claims": expected_claims}

    validator.validate_token.assert_awaited_once_with("valid-test-token")


def test_invalid_jwt_returns_401() -> None:
    """A JWT validation failure must be translated into HTTP 401."""

    validator = create_mock_validator()

    validator.validate_token.side_effect = JWTValidationError("JWT validation failed.")

    client = TestClient(create_test_app(validator))

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid-test-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token."
    assert response.headers["www-authenticate"] == "Bearer"

    validator.validate_token.assert_awaited_once_with("invalid-test-token")


def test_jwks_unavailable_returns_503() -> None:
    """A JWKS retrieval failure must be translated into HTTP 503."""

    validator = create_mock_validator()

    validator.validate_token.side_effect = JWKSUnavailableError(
        "Unable to retrieve trusted signing keys."
    )

    client = TestClient(create_test_app(validator))

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "Authentication service is temporarily unavailable."
    )

    validator.validate_token.assert_awaited_once_with("test-token")


def test_missing_jwt_validator_returns_503() -> None:
    """A missing application-level validator must return HTTP 503."""

    client = TestClient(create_test_app())

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Authentication service is unavailable."
