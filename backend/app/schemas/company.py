
"""Pydantic schemas for company registration requests and responses."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyCreateRequest(BaseModel):
    """Validate a company registration request."""

    company_name: str = Field(
        min_length=1,
        max_length=255,
    )

    @field_validator("company_name", mode="before")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        """Remove leading and trailing whitespace before validation."""
        if isinstance(value, str):
            return value.strip()

        return value


class CompanyResponse(BaseModel):
    """Expose the public details of a registered company."""

    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
    company_name: str
