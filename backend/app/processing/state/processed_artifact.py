from datetime import datetime

from pydantic import BaseModel


class ProcessedArtifact(BaseModel):
    """A successfully processed source artifact for a dataset/company/source scope.

    This model captures the historical artifact-level record needed to support
    later idempotency checks for previously successful processing runs.
    """

    dataset_name: str
    company_id: str | None = None
    source_id: str | None = None
    file_hash: str
    source_object_path: str
    successful_ingestion_id: str | None = None
    processed_at: datetime


__all__ = ["ProcessedArtifact"]
