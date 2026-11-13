"""Endpoint tests for the company registration API."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api.companies import router  # noqa: E402
from app.core.security.current_user import get_current_user  # noqa: E402
from app.db.dependencies import get_db  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture
def authenticated_user() -> User:
    """Provide a valid authenticated internal user for endpoint tests."""
    return User(
        user_id=uuid4(),
        keycloak_subject="keycloak-subject-123",
        email="owner@example.com",
        display_name="Test Owner",
    )


@pytest.fixture
def test_app(authenticated_user):
    """Create an isolated FastAPI app with the company router installed."""
    app = FastAPI()
    app.include_router(router)

    async def override_get_current_user():
        return authenticated_user

    async def override_get_db():
        yield MagicMock(spec=AsyncSession)

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    yield app

    app.dependency_overrides.clear()


def test_successful_company_registration(test_app, authenticated_user):
    """A valid authenticated request should create a company and return HTTP 201."""
    company_id = uuid4()
    company = SimpleNamespace(
        company_id=company_id,
        company_name="ABC Technologies",
    )
    service = MagicMock()
    service.register_company = AsyncMock(return_value=company)

    with patch("app.api.companies.CompanyRegistrationService", return_value=service) as service_class:
        with TestClient(test_app) as client:
            response = client.post(
                "/api/v1/companies",
                json={"company_name": "ABC Technologies"},
            )

    assert response.status_code == 201
    assert response.json() == {
        "company_id": str(company_id),
        "company_name": "ABC Technologies",
    }

    service_class.assert_called_once()
    service.register_company.assert_awaited_once_with(
        company_name="ABC Technologies",
        user_id=authenticated_user.user_id,
    )


def test_service_receives_internal_user_id_not_keycloak_subject(test_app, authenticated_user):
    """The endpoint must pass the internal UUID to the service, not the external subject."""
    company_id = uuid4()
    company = SimpleNamespace(
        company_id=company_id,
        company_name="Contoso",
    )
    service = MagicMock()
    service.register_company = AsyncMock(return_value=company)

    with patch("app.api.companies.CompanyRegistrationService", return_value=service):
        with TestClient(test_app) as client:
            client.post(
                "/api/v1/companies",
                json={"company_name": "Contoso"},
            )

    service.register_company.assert_awaited_once()
    called_kwargs = service.register_company.await_args.kwargs
    assert called_kwargs["company_name"] == "Contoso"
    assert called_kwargs["user_id"] == authenticated_user.user_id
    assert called_kwargs["user_id"] != authenticated_user.keycloak_subject


def test_company_name_whitespace_is_normalized_before_service_call(test_app, authenticated_user):
    """The schema should trim company names before validation and service invocation."""
    company_id = uuid4()
    company = SimpleNamespace(
        company_id=company_id,
        company_name="ABC Technologies",
    )
    service = MagicMock()
    service.register_company = AsyncMock(return_value=company)

    with patch("app.api.companies.CompanyRegistrationService", return_value=service):
        with TestClient(test_app) as client:
            response = client.post(
                "/api/v1/companies",
                json={"company_name": "  ABC Technologies  "},
            )

    assert response.status_code == 201
    service.register_company.assert_awaited_once_with(
        company_name="ABC Technologies",
        user_id=authenticated_user.user_id,
    )


def test_whitespace_only_company_name_is_rejected(test_app, authenticated_user):
    """Whitespace-only company names should fail validation before the service is called."""
    service = MagicMock()
    service.register_company = AsyncMock()

    with patch("app.api.companies.CompanyRegistrationService", return_value=service):
        with TestClient(test_app) as client:
            response = client.post(
                "/api/v1/companies",
                json={"company_name": "   "},
            )

    assert response.status_code == 422
    service.register_company.assert_not_awaited()


def test_unauthenticated_request_is_rejected(test_app):
    """The route must reject requests without an Authorization header."""
    service = MagicMock()
    service.register_company = AsyncMock()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides.clear()

    with patch("app.api.companies.CompanyRegistrationService", return_value=service):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/companies",
                json={"company_name": "ABC Technologies"},
            )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["detail"] == "Not authenticated."
    service.register_company.assert_not_awaited()


def test_company_name_exceeds_max_length_is_rejected(test_app, authenticated_user):
    """Names longer than the schema's 255-character limit should be rejected by Pydantic."""
    service = MagicMock()
    service.register_company = AsyncMock()

    with patch("app.api.companies.CompanyRegistrationService", return_value=service):
        with TestClient(test_app) as client:
            response = client.post(
                "/api/v1/companies",
                json={"company_name": "x" * 256},
            )

    assert response.status_code == 422
    service.register_company.assert_not_awaited()
