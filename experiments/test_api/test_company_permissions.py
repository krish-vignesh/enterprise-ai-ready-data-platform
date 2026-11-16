"""Unit tests for company permission policy and authorization dependency."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import company_authorization
from app.core.security.company_permissions import (
    COMPANY_ROLE_PERMISSIONS,
    CompanyPermission,
    role_has_permission,
)
from app.models.company_membership import CompanyRole


# ---------------------------------------------------------------------------
# Permission policy tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("role", "expected_permissions"),
    [
        (
            CompanyRole.OWNER,
            {
                CompanyPermission.VIEW_COMPANY_RESOURCES,
                CompanyPermission.CREATE_SOURCE_SYSTEM,
                CompanyPermission.CREATE_DATASET,
                CompanyPermission.UPLOAD_DOCUMENT,
                CompanyPermission.MANAGE_MEMBERS_AND_ROLES,
                CompanyPermission.DELETE_COMPANY,
            },
        ),
        (
            CompanyRole.ADMIN,
            {
                CompanyPermission.VIEW_COMPANY_RESOURCES,
                CompanyPermission.CREATE_SOURCE_SYSTEM,
                CompanyPermission.CREATE_DATASET,
                CompanyPermission.UPLOAD_DOCUMENT,
            },
        ),
        (
            CompanyRole.MEMBER,
            {
                CompanyPermission.VIEW_COMPANY_RESOURCES,
                CompanyPermission.CREATE_SOURCE_SYSTEM,
                CompanyPermission.UPLOAD_DOCUMENT,
            },
        ),
    ],
)
def test_role_permission_matrix(role, expected_permissions):
    """Verify every role receives exactly its approved permissions."""

    assert COMPANY_ROLE_PERMISSIONS[role] == frozenset(expected_permissions)

    for permission in CompanyPermission:
        assert role_has_permission(
            role,
            permission,
        ) is (permission in expected_permissions)


def test_unknown_role_has_no_permissions():
    """Verify an unknown role is denied every permission."""

    unknown_role = object()

    for permission in CompanyPermission:
        assert role_has_permission(unknown_role, permission) is False


# ---------------------------------------------------------------------------
# Company authorization dependency tests
# ---------------------------------------------------------------------------


@pytest.fixture
def authorization_context(monkeypatch):
    """Provide mocked repository, user, membership and database session."""

    user_id = uuid4()
    company_id = uuid4()

    current_user = SimpleNamespace(user_id=user_id)
    session = MagicMock()

    membership = SimpleNamespace(
        user_id=user_id,
        company_id=company_id,
        role=CompanyRole.MEMBER,
    )

    repository = MagicMock()
    repository.get_by_user_and_company = AsyncMock(
        return_value=membership,
    )

    repository_factory = MagicMock(return_value=repository)

    monkeypatch.setattr(
        company_authorization,
        "CompanyMembershipRepository",
        repository_factory,
    )

    return SimpleNamespace(
        user_id=user_id,
        company_id=company_id,
        current_user=current_user,
        session=session,
        membership=membership,
        repository=repository,
        repository_factory=repository_factory,
    )


@pytest.mark.asyncio
async def test_authorization_returns_membership_when_permission_is_granted(
    authorization_context,
):
    """Verify an authorized user receives their company membership."""

    context = authorization_context

    dependency = company_authorization.require_company_permission(
        CompanyPermission.CREATE_SOURCE_SYSTEM,
    )

    result = await dependency(
        company_id=context.company_id,
        current_user=context.current_user,
        session=context.session,
    )

    assert result is context.membership

    context.repository_factory.assert_called_once_with(context.session)

    context.repository.get_by_user_and_company.assert_awaited_once_with(
        user_id=context.user_id,
        company_id=context.company_id,
    )


@pytest.mark.asyncio
async def test_authorization_rejects_user_without_membership(
    authorization_context,
):
    """Verify a user without company membership receives HTTP 403."""

    context = authorization_context

    context.repository.get_by_user_and_company.return_value = None

    dependency = company_authorization.require_company_permission(
        CompanyPermission.VIEW_COMPANY_RESOURCES,
    )

    with pytest.raises(HTTPException) as exc_info:
        await dependency(
            company_id=context.company_id,
            current_user=context.current_user,
            session=context.session,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ("You are not authorized to perform this action.")


@pytest.mark.asyncio
async def test_authorization_rejects_member_without_required_permission(
    authorization_context,
):
    """Verify membership alone does not grant every company permission."""

    context = authorization_context

    dependency = company_authorization.require_company_permission(
        CompanyPermission.CREATE_DATASET,
    )

    with pytest.raises(HTTPException) as exc_info:
        await dependency(
            company_id=context.company_id,
            current_user=context.current_user,
            session=context.session,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == ("You are not authorized to perform this action.")


@pytest.mark.asyncio
async def test_authorization_propagates_repository_database_errors(
    authorization_context,
):
    """Verify database failures are not incorrectly converted into HTTP 403."""

    context = authorization_context

    context.repository.get_by_user_and_company.side_effect = RuntimeError(
        "Database unavailable",
    )

    dependency = company_authorization.require_company_permission(
        CompanyPermission.VIEW_COMPANY_RESOURCES,
    )

    with pytest.raises(RuntimeError, match="Database unavailable"):
        await dependency(
            company_id=context.company_id,
            current_user=context.current_user,
            session=context.session,
        )


@pytest.mark.asyncio
async def test_authorization_uses_requested_company_id(
    authorization_context,
):
    """Verify membership lookup uses the requested company and user IDs."""

    context = authorization_context

    requested_company_id = uuid4()

    dependency = company_authorization.require_company_permission(
        CompanyPermission.CREATE_SOURCE_SYSTEM,
    )

    await dependency(
        company_id=requested_company_id,
        current_user=context.current_user,
        session=context.session,
    )

    context.repository.get_by_user_and_company.assert_awaited_once_with(
        user_id=context.user_id,
        company_id=requested_company_id,
    )
