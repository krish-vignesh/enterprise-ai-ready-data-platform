
"""Service layer for Dataset catalog operations."""

import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset import (
    DatasetListItemResponse,
    DatasetResponse,
)
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_upload import DocumentResponse

logger = logging.getLogger(__name__)

DATASET_NAME_UNIQUE_CONSTRAINT = "uq_datasets_source_id_dataset_name"


class DatasetAlreadyExistsError(ValueError):
    """Raised when a Dataset name already exists under the same SourceSystem."""


def _get_constraint_name(error: IntegrityError) -> str | None:
    """Extract the database constraint name when the driver exposes it."""

    original_error = error.orig
    diagnostic = getattr(original_error, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)

    if isinstance(constraint_name, str):
        return constraint_name

    return None


class DatasetService:
    """Orchestrate Dataset creation and catalog operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with the request-scoped database session."""

        self.session = session
        self.dataset_repository = DatasetRepository(session)
        self.document_repository = DocumentRepository(session)

    async def create_dataset(
        self,
        *,
        source_id: UUID,
        dataset_name: str,
    ) -> Dataset:
        """Create a Dataset under an existing SourceSystem.

        Dataset names must be unique within their parent SourceSystem.
        The database unique constraint remains the final protection
        against concurrent duplicate creation requests.
        """

        try:
            existing_dataset = (
                await self.dataset_repository.get_by_source_and_name(
                    source_id,
                    dataset_name,
                )
            )

            if existing_dataset is not None:
                raise DatasetAlreadyExistsError(
                    "A dataset with this name already exists under this source system."
                )

            dataset = Dataset(
                source_id=source_id,
                dataset_name=dataset_name,
            )

            self.dataset_repository.add(dataset)

            await self.session.flush()
            await self.session.commit()

            logger.info(
                "dataset.creation.completed source_id=%s dataset_id=%s",
                source_id,
                dataset.dataset_id,
            )

            return dataset

        except DatasetAlreadyExistsError:
            await self.session.rollback()
            raise

        except IntegrityError as error:
            await self.session.rollback()

            if (
                _get_constraint_name(error)
                == DATASET_NAME_UNIQUE_CONSTRAINT
            ):
                logger.info(
                    "dataset.creation.duplicate_detected source_id=%s",
                    source_id,
                )

                raise DatasetAlreadyExistsError(
                    "A dataset with this name already exists under this source system."
                ) from error

            logger.exception(
                "dataset.creation.failed reason=integrity_error source_id=%s",
                source_id,
            )
            raise

        except Exception:
            await self.session.rollback()

            logger.exception(
                "dataset.creation.failed source_id=%s",
                source_id,
            )
            raise


    async def list_company_datasets(
        self,
        company_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[DatasetListItemResponse]:
        """List a company's datasets with aggregated document counts.

        COMPANY DATASET CATALOG ADDITION
        --------------------------------
        Purpose:
            Retrieve all datasets belonging to the requested company
            across its source systems.

        Data retrieval:
            Delegates company-scoped filtering, document aggregation,
            and pagination to DatasetRepository.

        Response transformation:
            Converts repository results into DatasetListItemResponse
            objects containing dataset metadata, total document count,
            and available document count.

        Security:
            The API authorization dependency verifies company membership
            and VIEW_COMPANY_RESOURCES permission before this method runs.
            The repository independently enforces company-level filtering.

        Transaction behaviour:
            This is a read-only operation. It does not commit, roll back,
            or start a new transaction.
        """

        rows = await self.dataset_repository.list_by_company_with_document_counts(
            company_id,
            limit=limit,
            offset=offset,
        )

        datasets = [
            DatasetListItemResponse(
                dataset_id=dataset.dataset_id,
                source_id=dataset.source_id,
                dataset_name=dataset.dataset_name,
                document_count=document_count,
                available_document_count=available_document_count,
            )
            for dataset, document_count, available_document_count in rows
        ]

        logger.debug(
            "dataset.list_company_datasets.completed "
            "company_id=%s limit=%s offset=%s result_count=%s",
            company_id,
            limit,
            offset,
            len(datasets),
        )

        return datasets


    async def get_dataset(
        self,
        dataset: Dataset,
    ) -> DatasetResponse:
        """Return the metadata of an authorized Dataset.

        DATASET DETAILS RETRIEVAL ADDITION
        ---------------------------------
        Purpose:
            Provide the metadata response for an individual Dataset.

        Authorization:
            The require_dataset_permission() FastAPI dependency
            retrieves the Dataset, resolves its owning company,
            and verifies the user's membership and permission
            before this service method is called.

        Data handling:
            Converts the already-authorized Dataset ORM object
            into the existing DatasetResponse Pydantic schema.

        Database access:
            No additional database query is performed because
            the authorization dependency supplies the resolved
            Dataset object.

        Response:
            Returns dataset_id, source_id, and dataset_name.

        This method does not retrieve document lists or document
        counts. Those responsibilities belong to separate endpoints.
        """

        return DatasetResponse.model_validate(dataset)

    async def list_dataset_documents(
        self,
        dataset: Dataset,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[DocumentResponse]:
        """List document metadata belonging to an authorized Dataset.

        DATASET DOCUMENT LISTING ADDITION
        ---------------------------------
        Purpose:
            Retrieve the registered documents belonging to a Dataset.

        Authorization:
            The require_dataset_permission() FastAPI dependency
            resolves the Dataset and verifies the user's company
            membership and VIEW_COMPANY_RESOURCES permission
            before this service method is called.

        Data retrieval:
            Delegates document retrieval, Dataset filtering,
            deterministic ordering, and pagination to
            DocumentRepository.list_by_dataset().

        Response transformation:
            Converts the retrieved Document ORM objects into
            the existing DocumentResponse Pydantic schema.

        Data exposure:
            Returns document metadata only. It does not expose
            original file contents, storage download operations,
            or processed-data previews.

        Transaction behaviour:
            This is a read-only operation. It does not commit,
            roll back, or start a new transaction.
        """

        documents = await self.document_repository.list_by_dataset(
            dataset.dataset_id,
            limit=limit,
            offset=offset,
        )

        document_responses = [
            DocumentResponse.model_validate(document)
            for document in documents
        ]

        logger.debug(
            "dataset.list_dataset_documents.completed "
            "dataset_id=%s limit=%s offset=%s result_count=%s",
            dataset.dataset_id,
            limit,
            offset,
            len(document_responses),
        )

        return document_responses



