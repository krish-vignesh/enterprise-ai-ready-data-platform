from __future__ import annotations

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType, TimestampType
from delta.tables import DeltaTable

from app.processing.state.processed_artifact import ProcessedArtifact
from app.spark.session import create_spark_session

PROCESSED_ARTIFACT_TABLE_PATH = "s3a://ai-data/processing/idempotency/"

PROCESSED_ARTIFACT_SCHEMA = StructType([
    StructField("dataset_name", StringType(), nullable=False),
    StructField("company_id", StringType(), nullable=True),
    StructField("source_id", StringType(), nullable=True),
    StructField("file_hash", StringType(), nullable=False),
    StructField("source_object_path", StringType(), nullable=False),
    StructField("successful_ingestion_id", StringType(), nullable=True),
    StructField("processed_at", TimestampType(), nullable=False),
])


def _coerce_spark_session(spark: SparkSession | None) -> SparkSession:
    if spark is None:
        return create_spark_session()
    if not isinstance(spark, SparkSession):
        raise TypeError(f"Expected a PySpark SparkSession, received {type(spark).__name__}.")
    return spark


def _table_missing_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "path does not exist" in message
        or "no such file" in message
        or "table or view not found" in message
        or ("analysisexception" in message and "path" in message and "does not exist" in message)
    )


def _to_row(artifact: ProcessedArtifact) -> dict[str, object]:
    if artifact is None:
        raise ValueError("artifact is required and cannot be None.")
    if not isinstance(artifact, ProcessedArtifact):
        raise TypeError(f"Expected a ProcessedArtifact, received {type(artifact).__name__}.")

    return {
        "dataset_name": artifact.dataset_name,
        "company_id": artifact.company_id,
        "source_id": artifact.source_id,
        "file_hash": artifact.file_hash,
        "source_object_path": artifact.source_object_path,
        "successful_ingestion_id": artifact.successful_ingestion_id,
        "processed_at": artifact.processed_at,
    }


def _artifact_identity_match(existing_df, incoming_df):
    dataset_match = F.col("existing.dataset_name") == F.col("incoming.dataset_name")
    company_match = (
        (F.col("existing.company_id") == F.col("incoming.company_id"))
        | (F.col("existing.company_id").isNull() & F.col("incoming.company_id").isNull())
    )
    source_match = (
        (F.col("existing.source_id") == F.col("incoming.source_id"))
        | (F.col("existing.source_id").isNull() & F.col("incoming.source_id").isNull())
    )
    file_hash_match = F.col("existing.file_hash") == F.col("incoming.file_hash")
    return dataset_match & company_match & source_match & file_hash_match


def processed_artifact_table_exists(
    spark: SparkSession | None = None,
    table_path: str = PROCESSED_ARTIFACT_TABLE_PATH,
) -> bool:
    """Check whether the ProcessedArtifact Delta table exists at the configured path."""
    resolved_spark = _coerce_spark_session(spark)

    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    try:
        resolved_spark.read.format("delta").load(table_path).limit(1).count()
        return True
    except Exception as exc:
        if _table_missing_error(exc):
            return False
        raise RuntimeError(
            "Failed to inspect the ProcessedArtifact Delta table at the provided path."
        ) from exc


def artifact_exists(
    artifact: ProcessedArtifact,
    spark: SparkSession | None = None,
    table_path: str = PROCESSED_ARTIFACT_TABLE_PATH,
) -> bool:
    """Return True when the exact logical artifact identity already exists in Delta."""
    if artifact is None:
        raise ValueError("artifact is required and cannot be None.")
    if not isinstance(artifact, ProcessedArtifact):
        raise TypeError(f"Expected a ProcessedArtifact, received {type(artifact).__name__}.")
    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    resolved_spark = _coerce_spark_session(spark)

    try:
        artifact_df = resolved_spark.read.format("delta").load(table_path)
    except Exception as exc:
        if _table_missing_error(exc):
            return False
        raise RuntimeError(
            "Failed to read the ProcessedArtifact Delta table from the provided path."
        ) from exc

    company_match = (
        (artifact_df.company_id == artifact.company_id)
        | (artifact_df.company_id.isNull() & F.lit(artifact.company_id).isNull())
    )
    source_match = (
        (artifact_df.source_id == artifact.source_id)
        | (artifact_df.source_id.isNull() & F.lit(artifact.source_id).isNull())
    )

    matching_rows = (
        artifact_df.filter(artifact_df.dataset_name == artifact.dataset_name)
        .filter(company_match)
        .filter(source_match)
        .filter(artifact_df.file_hash == artifact.file_hash)
        .limit(1)
        .collect()
    )
    return bool(matching_rows)


def write_processed_artifact(
    artifact: ProcessedArtifact,
    spark: SparkSession | None = None,
    table_path: str = PROCESSED_ARTIFACT_TABLE_PATH,
) -> None:
    """Record a successful processed artifact without duplicating the same identity."""
    if artifact is None:
        raise ValueError("artifact is required and cannot be None.")
    if not isinstance(artifact, ProcessedArtifact):
        raise TypeError(f"Expected a ProcessedArtifact, received {type(artifact).__name__}.")
    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    resolved_spark = _coerce_spark_session(spark)
    row = _to_row(artifact)
    incoming_df = resolved_spark.createDataFrame([row], schema=PROCESSED_ARTIFACT_SCHEMA)

    if not processed_artifact_table_exists(spark=resolved_spark, table_path=table_path):
        try:
            incoming_df.write.format("delta").mode("overwrite").save(table_path)
            return
        except Exception as exc:
            raise RuntimeError(
                "Failed to create the ProcessedArtifact Delta table at the provided path."
            ) from exc

    try:
        existing_df = resolved_spark.read.format("delta").load(table_path)
        delta_table = DeltaTable.forPath(resolved_spark, table_path)
        delta_table.alias("existing").merge(
            incoming_df.alias("incoming"),
            _artifact_identity_match(existing_df.alias("existing"), incoming_df.alias("incoming")),
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    except Exception as exc:
        raise RuntimeError(
            "Failed to persist the ProcessedArtifact Delta row to the existing table."
        ) from exc


__all__ = [
    "PROCESSED_ARTIFACT_TABLE_PATH",
    "PROCESSED_ARTIFACT_SCHEMA",
    "processed_artifact_table_exists",
    "artifact_exists",
    "write_processed_artifact",
]
