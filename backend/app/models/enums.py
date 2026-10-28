"""Enumerations used by the platform's database models."""

from enum import Enum


class DocumentStatus(str, Enum):
    """Represent the lifecycle state of a document."""

    UPLOADING = "UPLOADING"
    AVAILABLE = "AVAILABLE"
    FAILED = "FAILED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


class UploadAttemptStatus(str, Enum):
    """Represent the outcome of an individual upload attempt."""

    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
