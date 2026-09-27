from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SchemaColumn(BaseModel):
    """Structured representation of a dataset column in the source schema."""

    name: str = Field(..., description="Column name as it appears in the source dataset.")
    data_type: str = Field(..., description="Logical data type of the column.")
    nullable: bool = Field(default=True, description="Whether the column may contain null values.")
    description: str | None = Field(default=None, description="Optional business-friendly description.")


class BronzeIngestionMetadata(BaseModel):
    """Metadata contract for a single Bronze ingestion lineage event.

    The model captures the relationship between the original source artifact,
    the ingestion event, and the managed Bronze Delta table that represents the
    ingested data in the lakehouse.
    """

    ingestion_id: str = Field(..., description="Unique identifier for this ingestion event.")
    dataset_name: str = Field(..., description="Logical name of the dataset being ingested.")
    company_id: str = Field(..., description="Identifier of the company associated with the dataset.")
    company_name: str = Field(..., description="Human-readable company name.")

    source: str = Field(..., description="Originating source system or upload channel.")
    source_id: str = Field(..., description="Identifier of the source system or source channel that produced the data.")
    source_file_name: str = Field(..., description="Original filename supplied by the source.")
    source_format: str = Field(..., description="Original source format, such as csv or parquet.")
    source_object_path: str = Field(..., description="Object-storage path preserving the original source artifact.")
    file_size: int = Field(..., description="Size of the original source file in bytes.")
    file_hash: str = Field(..., description="Hash of the source file contents for deduplication and idempotency.")

    ingested_at: datetime = Field(
        ..., description="Timezone-aware timestamp when this ingestion was recorded."
    )

    schema_version: str = Field(..., description="Version of the dataset schema associated with this ingestion.")
    schema: list[SchemaColumn] = Field(..., description="Structured dataset schema including column names and types.")

    bronze_table_path: str | None = Field(
        default=None,
        description="Managed Bronze table location once it is created; may be unknown during early ingestion stages.",
    )

    ingestion_status: Literal["pending", "success", "failed"] = Field(
        default="pending",
        description="Lifecycle status of the ingestion.",
    )
    record_count: int | None = Field(
        default=None,
        description="Number of records written to the Bronze representation when available.",
    )

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": False,
    }
