
"""Pydantic schemas for document-upload API requests and responses."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import DocumentStatus
from app.services.document_upload_workflow import DocumentUploadOutcome


class DocumentResponse(BaseModel):
    """Expose safe, public document metadata."""

    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    dataset_id: UUID
    original_filename: str
    detected_format: str
    content_type: str | None
    file_size_bytes: int = Field(ge=0)
    sha256: str
    status: DocumentStatus


class DocumentUploadResponse(BaseModel):
    """Represent the result of a single document upload."""

    outcome: DocumentUploadOutcome
    document: DocumentResponse
    upload_attempt_id: UUID | None


class BatchDocumentUploadItemResponse(BaseModel):
    """Represent the outcome of one file in a batch upload."""

    filename: str
    outcome: DocumentUploadOutcome | Literal["FAILED"]
    document: DocumentResponse | None = None
    upload_attempt_id: UUID | None = None
    error_code: str | None = None
    error_message: str | None = None


class BatchDocumentUploadResponse(BaseModel):
    """Summarize the results of a batch document upload."""

    total_files: int = Field(ge=0)
    successful_uploads: int = Field(ge=0)
    already_available: int = Field(ge=0)
    in_progress: int = Field(ge=0)
    reconciliation_required: int = Field(ge=0)
    failed_uploads: int = Field(ge=0)
    results: list[BatchDocumentUploadItemResponse]

    @model_validator(mode="after")
    def validate_result_counts(self):
        """Ensure the summary counts match the individual results."""

        counts = {
            "successful_uploads": 0,
            "already_available": 0,
            "in_progress": 0,
            "reconciliation_required": 0,
            "failed_uploads": 0,
        }

        outcome_to_count = {
            DocumentUploadOutcome.UPLOADED: "successful_uploads",
            DocumentUploadOutcome.ALREADY_AVAILABLE: "already_available",
            DocumentUploadOutcome.UPLOAD_IN_PROGRESS: "in_progress",
            DocumentUploadOutcome.RECONCILIATION_REQUIRED:
                "reconciliation_required",
            "FAILED": "failed_uploads",
        }

        for result in self.results:
            counts[outcome_to_count[result.outcome]] += 1

        if self.total_files != len(self.results):
            raise ValueError(
                "total_files must match the number of results."
            )

        for field_name, expected_count in counts.items():
            if getattr(self, field_name) != expected_count:
                raise ValueError(
                    f"{field_name} does not match the individual results."
                )

        return self


class APIErrorResponse(BaseModel):
    """Provide a consistent public API error response."""

    error_code: str
    message: str
    request_id: UUID
