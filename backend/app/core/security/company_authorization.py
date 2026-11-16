"""FastAPI dependency for company membership and permission authorization."""

from collections.abc import Awaitable, Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.company_permissions import (
    CompanyPermission,
    role_has_permission,
)

from app.services.source_system_service import SourceSystemService
from app.core.security.current_user import get_current_user
from app.db.dependencies import get_db
from app.models.company_membership import CompanyMembership
from app.models.source_system import SourceSystem
from app.models.user import User
from app.repositories.company_membership_repository import (
    CompanyMembershipRepository,
)


def require_company_permission(
    permission: CompanyPermission,
) -> Callable[..., Awaitable[CompanyMembership]]:
    """Create a dependency that requires company membership and a permission."""

    async def company_permission_dependency(
        company_id: UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db)],
    ) -> CompanyMembership:
        """Authorize the current user for an operation within a company."""

        membership_repository = CompanyMembershipRepository(session)

        membership = await membership_repository.get_by_user_and_company(
            user_id=current_user.user_id,
            company_id=company_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action.",
            )

        if not role_has_permission(membership.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action.",
            )

        return membership

    return company_permission_dependency


def require_source_system_permission(permission: CompanyPermission):
    """Authorize access to a source system through its owning company."""

    async def permission_dependency(
        source_id: UUID,
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        session: Annotated[
            AsyncSession,
            Depends(get_db),
        ],
    ) -> SourceSystem:
        """Resolve the source system and verify company-level permission."""

        source_service = SourceSystemService(session)

        source = await source_service.get_source_system(source_id)

        if source is None:
            raise HTTPException(
                status_code=404,
                detail="Source system not found.",
            )

        membership = await CompanyMembershipRepository(session).get_by_user_and_company(
            user_id=current_user.user_id,
            company_id=source.company_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=404,
                detail="Source system not found.",
            )

        if not role_has_permission(membership.role, permission):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        return source

    return permission_dependency
