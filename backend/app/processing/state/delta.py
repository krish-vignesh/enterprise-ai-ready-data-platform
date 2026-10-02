from __future__ import annotations

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType, TimestampType
from delta.tables import DeltaTable

from app.processing.state.models import ProcessingState
from app.spark.session import create_spark_session

PROCESSING_STATE_TABLE_PATH = "s3a://ai-data/processing/state/"

PROCESSING_STATE_SCHEMA = StructType([
    StructField("dataset_name", StringType(), nullable=False),
    StructField("company_id", StringType(), nullable=True),
    StructField("source_id", StringType(), nullable=True),
    StructField("last_successful_ingestion_id", StringType(), nullable=True),
    StructField("last_successful_file_hash", StringType(), nullable=True),
    StructField("last_successful_source_object_path", StringType(), nullable=True),
    StructField("last_successful_ingested_at", TimestampType(), nullable=True),
    StructField("updated_at", TimestampType(), nullable=False),
])


def _coerce_spark_session(spark: SparkSession | None) -> SparkSession:
    if spark is None:
        return create_spark_session()
    if not isinstance(spark, SparkSession):
        raise TypeError(f"Expected a PySpark SparkSession, received {type(spark).__name__}.")
    return spark


def _processing_state_to_row(state: ProcessingState) -> dict[str, object]:
    if state is None:
        raise ValueError("state is required and cannot be None.")
    if not isinstance(state, ProcessingState):
        raise TypeError(f"Expected a ProcessingState, received {type(state).__name__}.")

    return {
        "dataset_name": state.dataset_name,
        "company_id": state.company_id,
        "source_id": state.source_id,
        "last_successful_ingestion_id": state.last_successful_ingestion_id,
        "last_successful_file_hash": state.last_successful_file_hash,
        "last_successful_source_object_path": state.last_successful_source_object_path,
        "last_successful_ingested_at": state.last_successful_ingested_at,
        "updated_at": state.updated_at,
    }


def _state_scope_match(existing_df, incoming_df):
    dataset_match = F.col("existing.dataset_name") == F.col("incoming.dataset_name")
    company_match = (
        (F.col("existing.company_id") == F.col("incoming.company_id"))
        | (F.col("existing.company_id").isNull() & F.col("incoming.company_id").isNull())
    )
    source_match = (
        (F.col("existing.source_id") == F.col("incoming.source_id"))
        | (F.col("existing.source_id").isNull() & F.col("incoming.source_id").isNull())
    )
    return dataset_match & company_match & source_match


def _table_missing_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "path does not exist" in message
        or "no such file" in message
        or "table or view not found" in message
        or ("analysisexception" in message and "path" in message and "does not exist" in message)
    )


def write_processing_state(
    state: ProcessingState,
    spark: SparkSession | None = None,
    table_path: str = PROCESSING_STATE_TABLE_PATH,
) -> None:
    """Persist a ProcessingState row without overwriting other dataset/source scopes."""
    resolved_spark = _coerce_spark_session(spark)

    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    row = _processing_state_to_row(state)
    incoming_df = resolved_spark.createDataFrame([row], schema=PROCESSING_STATE_SCHEMA)

    if not state_table_exists(spark=resolved_spark, table_path=table_path):
        try:
            incoming_df.write.format("delta").mode("overwrite").save(table_path)
            return
        except Exception as exc:
            raise RuntimeError(
                "Failed to create the ProcessingState Delta table at the provided path."
            ) from exc

    try:
        existing_df = resolved_spark.read.format("delta").load(table_path)
        delta_table = DeltaTable.forPath(resolved_spark, table_path)
        delta_table.alias("existing").merge(
            incoming_df.alias("incoming"),
            _state_scope_match(existing_df.alias("existing"), incoming_df.alias("incoming")),
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    except Exception as exc:
        raise RuntimeError(
            "Failed to persist the ProcessingState Delta row to the existing table."
        ) from exc


def read_processing_state(
    dataset_name: str,
    spark: SparkSession | None = None,
    table_path: str = PROCESSING_STATE_TABLE_PATH,
    *,
    company_id: str | None = None,
    source_id: str | None = None,
) -> ProcessingState | None:
    """Read the last persisted ProcessingState for a dataset scope, if any."""
    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("dataset_name is required and must be a non-empty string.")
    if company_id is not None and (not isinstance(company_id, str) or not company_id.strip()):
        raise ValueError("company_id must be a non-empty string when provided.")
    if source_id is not None and (not isinstance(source_id, str) or not source_id.strip()):
        raise ValueError("source_id must be a non-empty string when provided.")
    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    resolved_spark = _coerce_spark_session(spark)

    try:
        state_df = resolved_spark.read.format("delta").load(table_path)
    except Exception as exc:
        if _table_missing_error(exc):
            return None
        raise RuntimeError(
            "Failed to read the ProcessingState Delta table from the provided path."
        ) from exc

    query = state_df.filter(state_df.dataset_name == dataset_name)
    if company_id is not None:
        query = query.filter(state_df.company_id == company_id)
    else:
        query = query.filter(state_df.company_id.isNull())
    if source_id is not None:
        query = query.filter(state_df.source_id == source_id)
    else:
        query = query.filter(state_df.source_id.isNull())

    rows = query.orderBy(state_df.updated_at.desc()).limit(1).collect()
    if not rows:
        return None

    row = rows[0].asDict()
    try:
        return ProcessingState(**row)
    except Exception as exc:
        raise RuntimeError(
            "Failed to convert the persisted ProcessingState Delta record into a ProcessingState model."
        ) from exc


def state_table_exists(
    spark: SparkSession | None = None,
    table_path: str = PROCESSING_STATE_TABLE_PATH,
) -> bool:
    """Check whether the ProcessingState Delta table exists at the configured path."""
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
            "Failed to inspect the ProcessingState Delta table at the provided path."
        ) from exc


__all__ = [
    "PROCESSING_STATE_TABLE_PATH",
    "write_processing_state",
    "read_processing_state",
    "state_table_exists",
]
