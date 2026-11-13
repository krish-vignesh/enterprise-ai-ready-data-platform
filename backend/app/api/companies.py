
"""API routes for company registration."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.current_user import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.company import CompanyCreateRequest, CompanyResponse
from app.services.company_registration_service import (
    CompanyRegistrationService,
)


router = APIRouter(prefix="/api/v1", tags=["Companies"])


@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=201,
)
async def register_company(
    company_data: CompanyCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    """Register a company for the authenticated user."""

    company_service = CompanyRegistrationService(session)

    company = await company_service.register_company(
        company_name=company_data.company_name,
        user_id=current_user.user_id,
    )

    return CompanyResponse.model_validate(company)
