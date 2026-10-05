from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.lakehouse.bronze.pipeline import run_bronze_ingestion
from app.lakehouse.bronze.source import SourceArtifact
from app.lakehouse.silver.pipeline import run_silver_pipeline
from app.processing.state.delta import write_processing_state
from app.processing.state.idempotency import artifact_exists, write_processed_artifact
from app.processing.state.models import ProcessingState
from app.processing.state.processed_artifact import ProcessedArtifact
from app.spark.session import create_spark_session
from app.storage.ingest import save_data, save_file


def ingest_data(request): #Service travel in the route to storage
    file_path = save_data(request)
    return {
        "status": "completed",
        "message": f"Data {request.dataset}ingestion completed successfully"
    }


def ingest_file_data(metadata, file):
    file_path = save_file(metadata, file)

    return {
        "status": "completed",
        "message": f"File {metadata.dataset} ingestion completed successfully"
    }


def process_source_artifact(
    source_artifact: SourceArtifact,
    dataset_name: str,
    source: str,
    source_format: str,
    source_object_path: str,
    file_size: int,
    file_hash: str,
    *,
    spark: Any | None = None,
    bronze_table_path: str | None = None,
    silver_table_path: str | None = None,
    schema_version: str = "v1",
    source_file_name: str | None = None,
    ingestion_id: str | None = None,
    bronze_mode: str = "overwrite",
    silver_mode: str = "overwrite",
) -> dict[str, Any]:
    """Coordinate Bronze + Silver execution for a single identified source artifact.

    The orchestration layer is intentionally narrow: it checks the historical
    artifact ledger for duplicate successful processing, delegates Bronze and
    Silver execution to their existing functions, and records successful
    completion only after both stages finish successfully.
    """
    if source_artifact is None:
        raise ValueError("source_artifact is required to process a source artifact.")
    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("dataset_name is required and must be a non-empty string.")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source is required and must be a non-empty string.")
    if not isinstance(source_format, str) or not source_format.strip():
        raise ValueError("source_format is required and must be a non-empty string.")
    if not isinstance(source_object_path, str) or not source_object_path.strip():
        raise ValueError("source_object_path is required and must be a non-empty string.")
    if file_size is None:
        raise ValueError("file_size is required before processing an artifact.")
    if not isinstance(file_hash, str) or not file_hash.strip():
        raise ValueError("file_hash is required and must be a non-empty string.")
    if silver_table_path is None or not str(silver_table_path).strip():
        raise ValueError("silver_table_path is required and must be a non-empty string.")

    resolved_spark = spark if spark is not None else create_spark_session()

    artifact_record = ProcessedArtifact(
        dataset_name=dataset_name,
        company_id=source_artifact.company_id,
        source_id=source_artifact.source_id,
        file_hash=file_hash,
        source_object_path=source_object_path,
        successful_ingestion_id=None,
        processed_at=datetime.now(timezone.utc),
    )

    if artifact_exists(artifact_record, spark=resolved_spark):
        return {
            "status": "SKIP",
            "reason": "artifact already successfully processed",
            "dataset_name": dataset_name,
            "company_id": source_artifact.company_id,
            "source_id": source_artifact.source_id,
            "file_hash": file_hash,
        }

    bronze_result = run_bronze_ingestion(
        spark=resolved_spark,
        source_artifact=source_artifact,
        dataset_name=dataset_name,
        source=source,
        source_format=source_format,
        source_object_path=source_object_path,
        source_file_name=source_file_name,
        file_size=file_size,
        file_hash=file_hash,
        schema_version=schema_version,
        bronze_table_path=bronze_table_path,
        mode=bronze_mode,
        ingestion_id=ingestion_id,
    )

    if bronze_result.get("status") != "success":
        raise RuntimeError(f"Bronze ingestion did not finish successfully for dataset '{dataset_name}'.")

    silver_result = run_silver_pipeline(
        spark=resolved_spark,
        bronze_table_path=bronze_result["bronze_table_path"],
        silver_table_path=silver_table_path,
        dataset_name=dataset_name,
        mode=silver_mode,
    )

    success_time = datetime.now(timezone.utc)
    successful_artifact = ProcessedArtifact(
        dataset_name=dataset_name,
        company_id=source_artifact.company_id,
        source_id=source_artifact.source_id,
        file_hash=file_hash,
        source_object_path=source_object_path,
        successful_ingestion_id=bronze_result["ingestion_id"],
        processed_at=success_time,
    )
    write_processed_artifact(successful_artifact, spark=resolved_spark)

    write_processing_state(
        ProcessingState(
            dataset_name=dataset_name,
            company_id=source_artifact.company_id,
            source_id=source_artifact.source_id,
            last_successful_ingestion_id=bronze_result["ingestion_id"],
            last_successful_file_hash=file_hash,
            last_successful_source_object_path=source_object_path,
            last_successful_ingested_at=success_time,
            updated_at=success_time,
        ),
        spark=resolved_spark,
    )

    return {
        "status": "SUCCESS",
        "dataset_name": dataset_name,
        "company_id": source_artifact.company_id,
        "source_id": source_artifact.source_id,
        "file_hash": file_hash,
        "bronze_result": bronze_result,
        "silver_result": silver_result,
        "processed_artifact": successful_artifact.model_dump(mode="json"),
    }


__all__ = [
    "ingest_data",
    "ingest_file_data",
    "process_source_artifact",
]
