from __future__ import annotations

from typing import Literal

from pyspark.sql import DataFrame, SparkSession


WriteMode = Literal["append", "overwrite", "errorifexists"]


def write_bronze_delta(
    df: DataFrame,
    table_path: str,
    mode: WriteMode = "append",
    partition_by: list[str] | None = None,
) -> None:
    """Write a Spark DataFrame to a managed Bronze Delta table at the supplied path.

    The path is intentionally storage-agnostic; callers provide a lakehouse URI such as
    s3a://ai-data/bronze/tables/<dataset>/.
    """
    writer = df.write.format("delta").mode(mode)
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    writer.save(table_path)


def read_bronze_delta(spark: SparkSession, table_path: str) -> DataFrame:
    """Read a Bronze Delta table from the supplied storage path into a Spark DataFrame."""
    return spark.read.format("delta").load(table_path)


def table_exists(spark: SparkSession, table_path: str) -> bool:
    """Check whether a Delta table exists at the given storage path."""
    try:
        spark.read.format("delta").load(table_path).limit(1).count()
        return True
    except Exception:
        return False
