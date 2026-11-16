"""API routes for source-system catalog operations."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.company_authorization import (
    require_company_permission,
    require_source_system_permission,
)
from app.core.security.company_permissions import CompanyPermission
from app.db.dependencies import get_db
from app.models.source_system import SourceSystem
from app.schemas.source_system import (
    SourceSystemCreateRequest,
    SourceSystemCreateResponse,
    SourceSystemResponse,
)
from app.services.source_system_service import SourceSystemService


router = APIRouter(prefix="/api/v1", tags=["Source Systems"])


@router.post(
    "/companies/{company_id}/source-systems",
    response_model=SourceSystemCreateResponse,
    status_code=201,
    dependencies=[
        Depends(require_company_permission(CompanyPermission.CREATE_SOURCE_SYSTEM))
    ],
)
async def create_source_system(
    company_id: UUID,
    source_data: SourceSystemCreateRequest,
    session: AsyncSession = Depends(get_db),
) -> SourceSystemCreateResponse:
    """Create a source system within an authorized company."""

    source_service = SourceSystemService(session)

    source = await source_service.create_source_system(
        company_id=company_id,
        source_name=source_data.source_name,
        source_type=source_data.source_type,
    )

    return SourceSystemCreateResponse.model_validate(source)


@router.get(
    "/companies/{company_id}/source-systems",
    response_model=list[SourceSystemResponse],
    dependencies=[
        Depends(require_company_permission(CompanyPermission.VIEW_COMPANY_RESOURCES))
    ],
)
async def list_source_systems(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> list[SourceSystemResponse]:
    """List source systems belonging to an authorized company."""

    source_service = SourceSystemService(session)

    sources = await source_service.list_source_systems(
        company_id,
        limit=limit,
        offset=offset,
    )

    return [SourceSystemResponse.model_validate(source) for source in sources]


@router.get(
    "/source-systems/{source_id}",
    response_model=SourceSystemResponse,
)
async def get_source_system(
    source: SourceSystem = Depends(
        require_source_system_permission(CompanyPermission.VIEW_COMPANY_RESOURCES)
    ),
) -> SourceSystemResponse:
    """Retrieve one source system after verifying company access."""

    return SourceSystemResponse.model_validate(source)
