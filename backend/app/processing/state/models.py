from datetime import datetime

from pydantic import BaseModel


class ProcessingState(BaseModel):
    """
    Persistent state describing the last successfully processed
    ingestion for a dataset/source scope.
    """

    dataset_name: str
    company_id: str | None = None
    source_id: str | None = None

    last_successful_ingestion_id: str | None = None
    last_successful_file_hash: str | None = None
    last_successful_source_object_path: str | None = None
    last_successful_ingested_at: datetime | None = None

    updated_at: datetime
