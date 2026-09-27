from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pyspark.sql import DataFrame, SparkSession

from app.lakehouse.bronze.delta import WriteMode, write_bronze_delta
from app.lakehouse.bronze.metadata import BronzeIngestionMetadata, SchemaColumn
from app.lakehouse.bronze.source import SourceArtifact
from app.spark.io.reader import read_data
from app.spark.session import create_spark_session


def _build_bronze_table_path(dataset_name: str, bronze_table_root: str = "s3a://ai-data/bronze/tables") -> str:
    """Return the dataset-level Bronze Delta path for a logical dataset."""
    cleaned_name = dataset_name.strip("/")
    return f"{bronze_table_root.rstrip('/')}/{cleaned_name}/"


def _schema_to_metadata(df: DataFrame) -> list[SchemaColumn]:
    """Convert a Spark DataFrame schema to the Bronze metadata schema contract."""
    return [
        SchemaColumn(
            name=field.name,
            data_type=str(field.dataType),
            nullable=field.nullable,
        )
        for field in df.schema.fields
    ]


def _validate_source_artifact(source_artifact: SourceArtifact) -> None:
    """Ensure source metadata is present before continuing the Bronze workflow."""
    if source_artifact is None:
        raise ValueError("source_artifact is required to coordinate Bronze ingestion.")

    required_fields = {
        "company_id": source_artifact.company_id,
        "company_name": source_artifact.company_name,
        "source_id": source_artifact.source_id,
        "source_object_path": source_artifact.source_object_path,
    }

    missing = [name for name, value in required_fields.items() if value is None or str(value).strip() == ""]
    if missing:
        raise ValueError(
            "Missing required source metadata for Bronze ingestion: " + ", ".join(missing)
        )


def run_bronze_ingestion(
    spark: SparkSession | None,
    source_artifact: SourceArtifact,
    dataset_name: str,
    source: str,
    source_format: str,
    source_object_path: str,
    *,
    source_file_name: str | None = None,
    file_size: int | None = None,
    file_hash: str | None = None,
    schema_version: str = "v1",
    bronze_table_root: str = "s3a://ai-data/bronze/tables",
    bronze_table_path: str | None = None,
    df: DataFrame | None = None,
    read_options: dict[str, Any] | None = None,
    mode: WriteMode = "overwrite",
    ingestion_id: str | None = None,
) -> dict[str, Any]:
    """Coordinate a Bronze ingestion from source artifact to managed Delta table.

    The function keeps orchestration responsibilities limited to preparing the
    ingestion context, reading a Spark DataFrame, writing it to the Bronze Delta
    table, and updating the metadata record to reflect success or failure.
    """
    if spark is None:
        spark = create_spark_session()

    if not dataset_name or not str(dataset_name).strip():
        raise ValueError("dataset_name is required for Bronze ingestion.")
    if not source or not str(source).strip():
        raise ValueError("source is required for Bronze ingestion.")
    if not source_format or not str(source_format).strip():
        raise ValueError("source_format is required for Bronze ingestion.")
    if not source_object_path or not str(source_object_path).strip():
        raise ValueError("source_object_path is required for Bronze ingestion.")

    _validate_source_artifact(source_artifact)

    if file_size is None:
        raise ValueError("file_size is required upstream metadata for Bronze ingestion.")
    if file_hash is None or str(file_hash).strip() == "":
        raise ValueError("file_hash is required upstream metadata for Bronze ingestion.")

    resolved_ingestion_id = ingestion_id or str(uuid4())
    resolved_bronze_table_path = bronze_table_path or _build_bronze_table_path(dataset_name, bronze_table_root)
    resolved_file_name = source_file_name or str(Path(source_object_path.rstrip("/")).name or "source-file")

    metadata = BronzeIngestionMetadata(
        ingestion_id=resolved_ingestion_id,
        dataset_name=dataset_name,
        company_id=source_artifact.company_id,
        company_name=source_artifact.company_name,
        source=source,
        source_id=source_artifact.source_id,
        source_file_name=resolved_file_name,
        source_format=str(source_format).lower(),
        source_object_path=source_object_path,
        file_size=file_size,
        file_hash=file_hash,
        ingested_at=datetime.now(timezone.utc),
        schema_version=schema_version,
        schema=[],
        bronze_table_path=resolved_bronze_table_path,
        ingestion_status="pending",
        record_count=None,
    )

    try:
        if df is None:
            df = read_data(spark, source_object_path, source_format, options=read_options)

        metadata.schema = _schema_to_metadata(df)
        write_bronze_delta(df, resolved_bronze_table_path, mode=mode)
        record_count = int(df.count())

        metadata.bronze_table_path = resolved_bronze_table_path
        metadata.record_count = record_count
        metadata.ingestion_status = "success"

        return {
            "ingestion_id": metadata.ingestion_id,
            "status": metadata.ingestion_status,
            "dataset_name": metadata.dataset_name,
            "bronze_table_path": metadata.bronze_table_path,
            "record_count": metadata.record_count,
            "metadata": metadata.model_dump(mode="json"),
        }
    except Exception as exc:  # pragma: no cover - surfaced to caller for observability.
        metadata.ingestion_status = "failed"
        metadata.record_count = None
        raise RuntimeError(
            f"Bronze ingestion failed for dataset '{dataset_name}' with ingestion_id '{resolved_ingestion_id}'."
        ) from exc


__all__ = ["run_bronze_ingestion"]
