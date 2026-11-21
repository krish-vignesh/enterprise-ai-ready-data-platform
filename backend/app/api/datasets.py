"""API routes for Dataset catalog operations."""

import logging

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.core.security.company_authorization import (
    require_company_permission,
    require_source_system_permission,
    require_dataset_permission
)
from app.core.security.company_permissions import CompanyPermission
from app.models.source_system import SourceSystem
from app.schemas.dataset import (
    DatasetCreateRequest,
    DatasetCreateResponse,
    DatasetListItemResponse,
    DatasetResponse,
)
from app.models.dataset import Dataset
from app.services.dataset_service import (
    DatasetAlreadyExistsError,
    DatasetService,
)
from app.schemas.document_upload import DocumentResponse


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Datasets"],
)


@router.post(
    "/source-systems/{source_id}/datasets",
    response_model=DatasetCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dataset(
    payload: DatasetCreateRequest,
    source: SourceSystem = Depends(
        require_source_system_permission(
            CompanyPermission.CREATE_DATASET
        )
    ),
    session: AsyncSession = Depends(get_db),
) -> DatasetCreateResponse:
    """Create a Dataset under an authorized SourceSystem.

    Authorization:
        Verifies company membership and CREATE_DATASET permission
        through the SourceSystem authorization dependency.

    Processing:
        Delegates Dataset creation and duplicate handling
        to DatasetService.

    Response:
        Returns the newly created Dataset with HTTP 201.
    """

    dataset_service = DatasetService(session)

    try:
        dataset = await dataset_service.create_dataset(
            source_id=source.source_id,
            dataset_name=payload.dataset_name,
        )

    except DatasetAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return DatasetCreateResponse.model_validate(dataset)


@router.get(
    "/companies/{company_id}/datasets",
    response_model=list[DatasetListItemResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_company_permission(
                CompanyPermission.VIEW_COMPANY_RESOURCES
            )
        )
    ],
)
async def list_company_datasets(
    company_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> list[DatasetListItemResponse]:
    """List all Datasets belonging to an authorized Company.

    Authorization:
        Verifies that the authenticated user belongs to the
        requested Company and has VIEW_COMPANY_RESOURCES permission.

    Data retrieval:
        Delegates company-scoped filtering, document aggregation,
        and pagination to DatasetService.

    Response:
        Returns Dataset metadata with total and available
        document counts.
    """

    dataset_service = DatasetService(session)

    datasets = await dataset_service.list_company_datasets(
        company_id,
        limit=limit,
        offset=offset,
    )

    return datasets

@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_dataset(
    dataset: Dataset = Depends(
        require_dataset_permission(
            CompanyPermission.VIEW_COMPANY_RESOURCES
        )
    ),
    session: AsyncSession = Depends(get_db),
) -> DatasetResponse:
    """Retrieve metadata for an authorized Dataset.

    Authorization:
        Verifies company membership and VIEW_COMPANY_RESOURCES
        permission through the Dataset authorization dependency.

    Data retrieval:
        Uses the already-authorized Dataset object returned
        by the authorization dependency.

    Response:
        Returns Dataset metadata without document counts
        or document listings.
    """

    dataset_service = DatasetService(session)

    return await dataset_service.get_dataset(dataset)

@router.get(
    "/datasets/{dataset_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_dataset_documents(
    dataset: Dataset = Depends(
        require_dataset_permission(
            CompanyPermission.VIEW_COMPANY_RESOURCES
        )
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    """List document metadata belonging to an authorized Dataset.

    Authorization:
        Verifies company membership and VIEW_COMPANY_RESOURCES
        permission through the Dataset authorization dependency.

    Data retrieval:
        Delegates document retrieval, filtering, ordering,
        and pagination to DatasetService.

    Response:
        Returns registered document metadata only.
        Original file contents and download operations
        are not exposed by this endpoint.
    """

    dataset_service = DatasetService(session)

    documents = await dataset_service.list_dataset_documents(
        dataset,
        limit=limit,
        offset=offset,
    )

    return documents
