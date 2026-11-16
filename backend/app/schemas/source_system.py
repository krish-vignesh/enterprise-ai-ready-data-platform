"""Pydantic schemas for source-system catalog requests and responses."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceSystemCreateRequest(BaseModel):
    """Validate a source-system creation request."""

    source_name: str = Field(
        min_length=1,
        max_length=255,
    )

    source_type: str = Field(
        min_length=1,
        max_length=64,
    )

    @field_validator("source_name", "source_type", mode="before")
    @classmethod
    def normalize_string_fields(cls, value: str) -> str:
        """Remove leading and trailing whitespace before validation."""

        if isinstance(value, str):
            return value.strip()

        return value


class SourceSystemResponse(BaseModel):
    """Expose the public details of a source system."""

    model_config = ConfigDict(from_attributes=True)

    source_id: UUID
    company_id: UUID
    source_name: str
    source_type: str


class SourceSystemCreateResponse(SourceSystemResponse):
    """Confirm successful source-system creation."""

    message: str = "Source system created successfully"
