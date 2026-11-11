"""FastAPI dependency for resolving the authenticated platform user."""

from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.authentication import get_token_claims
from app.db.dependencies import get_db
from app.models.user import User
from app.services.identity_service import IdentityService


async def get_current_user(
    token_claims: Annotated[
        dict[str, Any],
        Depends(get_token_claims),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> User:
    """Resolve or provision the internal user from validated token claims."""

    keycloak_subject: str = token_claims["sub"]

    email_claim = token_claims.get("email")
    email = (
        email_claim if isinstance(email_claim, str) and email_claim.strip() else None
    )

    display_name_claim = token_claims.get("name")
    display_name = (
        display_name_claim
        if isinstance(display_name_claim, str) and display_name_claim.strip()
        else None
    )

    identity_service = IdentityService(session)

    return await identity_service.resolve_or_provision_user(
        keycloak_subject=keycloak_subject,
        email=email,
        display_name=display_name,
    )
