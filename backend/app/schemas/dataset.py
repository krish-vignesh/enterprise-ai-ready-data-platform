
"""Pydantic schemas for dataset catalog requests and responses."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DatasetCreateRequest(BaseModel):
    """Validate a dataset creation request."""

    dataset_name: str = Field(
        min_length=1,
        max_length=255,
    )

    @field_validator("dataset_name", mode="before")
    @classmethod
    def normalize_dataset_name(cls, value: str) -> str:
        """Remove leading and trailing whitespace before validation."""

        if isinstance(value, str):
            return value.strip()

        return value


class DatasetResponse(BaseModel):
    """Expose the public details of a dataset."""

    model_config = ConfigDict(from_attributes=True)

    dataset_id: UUID
    source_id: UUID
    dataset_name: str


class DatasetCreateResponse(DatasetResponse):
    """Confirm successful dataset creation."""

    message: str = "Dataset created successfully"


class DatasetListItemResponse(DatasetResponse):
    """Represent a dataset with its document counts."""

    document_count: int = Field(ge=0)
    available_document_count: int = Field(ge=0)
