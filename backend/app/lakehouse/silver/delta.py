from __future__ import annotations

from typing import Literal

from pyspark.sql import DataFrame, SparkSession


WriteMode = Literal["append", "overwrite", "errorifexists"]


def write_silver_delta(
    df: DataFrame,
    table_path: str,
    mode: WriteMode = "append",
    partition_by: list[str] | None = None,
) -> None:
    """Write a Spark DataFrame to a Silver Delta table at the supplied path."""

    if df is None:
        raise ValueError("DataFrame argument is required and cannot be None.")
    if not isinstance(df, DataFrame):
        raise TypeError(f"Expected a PySpark DataFrame, received {type(df).__name__}.")

    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")
    if mode not in {"append", "overwrite", "errorifexists"}:
        raise ValueError("mode must be one of: append, overwrite, errorifexists.")

    if partition_by is not None:
        if not isinstance(partition_by, list):
            raise TypeError("partition_by must be a list of column names or None.")
        for column_name in partition_by:
            if not isinstance(column_name, str) or not column_name.strip():
                raise ValueError("partition_by entries must be non-empty column names.")

    try:
        writer = df.write.format("delta").mode(mode)
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        writer.save(table_path)
    except Exception as exc:
        raise RuntimeError(
            "Failed to write the provided PySpark DataFrame to the Silver Delta table."
        ) from exc


def read_silver_delta(spark: SparkSession, table_path: str) -> DataFrame:
    """Read a Silver Delta table from the supplied storage path into a Spark DataFrame."""

    if spark is None:
        raise ValueError("SparkSession argument is required and cannot be None.")
    if not isinstance(spark, SparkSession):
        raise TypeError(f"Expected a PySpark SparkSession, received {type(spark).__name__}.")
    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    try:
        return spark.read.format("delta").load(table_path)
    except Exception as exc:
        raise RuntimeError(
            "Failed to read the Silver Delta table from the provided path."
        ) from exc


def table_exists(spark: SparkSession, table_path: str) -> bool:
    """Check whether a Delta table exists at the given storage path."""

    if spark is None:
        raise ValueError("SparkSession argument is required and cannot be None.")
    if not isinstance(spark, SparkSession):
        raise TypeError(f"Expected a PySpark SparkSession, received {type(spark).__name__}.")
    if not isinstance(table_path, str) or not table_path.strip():
        raise ValueError("table_path is required and must be a non-empty string.")

    try:
        spark.read.format("delta").load(table_path).limit(1).count()
        return True
    except Exception:
        return False


__all__ = ["WriteMode", "write_silver_delta", "read_silver_delta", "table_exists"]
