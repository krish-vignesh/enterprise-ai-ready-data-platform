from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import NumericType


@dataclass(frozen=True)
class ColumnProfile:
    """Summary of the data quality characteristics for one column."""

    column_name: str
    data_type: str
    nullable: bool
    null_count: int
    null_percentage: float
    distinct_count: int
    minimum: int | float | Decimal | None = None
    maximum: int | float | Decimal | None = None
    mean: float | None = None


@dataclass(frozen=True)
class DatasetProfile:
    """Reusable structure describing a dataset profile generated from a PySpark DataFrame."""

    row_count: int
    column_count: int
    exact_duplicate_row_count: int
    columns: list[ColumnProfile] = field(default_factory=list)


def _is_numeric_type(data_type: Any) -> bool:
    """Return True when the Spark data type is numeric."""

    return isinstance(data_type, NumericType)


def _numeric_column_names(dataframe: DataFrame) -> list[str]:
    """List columns whose Spark schema type is numeric."""

    numeric_columns: list[str] = []
    for field in dataframe.schema.fields:
        if _is_numeric_type(field.dataType):
            numeric_columns.append(field.name)
    return numeric_columns


def _duplicate_row_count(dataframe: DataFrame, row_count: int | None = None) -> int:
    """Count exact duplicate rows beyond the first occurrence for each duplicate group."""

    if row_count is None:
        row_count = int(dataframe.count())

    if row_count == 0:
        return 0
    if not dataframe.columns:
        return max(row_count - 1, 0)

    duplicate_groups = (
        dataframe.groupBy(*dataframe.columns)
        .count()
        .filter(F.col("count") > 1)
    )
    duplicate_rows = duplicate_groups.agg(F.sum(F.col("count") - 1).cast("long").alias("duplicate_rows"))
    value = duplicate_rows.collect()[0][0]
    return int(value or 0)


def _profile_column_aggregates(dataframe: DataFrame) -> dict[str, tuple[int, int]]:
    """Compute null and distinct counts for each column in a single pass."""

    if not dataframe.columns:
        return {}

    aggregates: list[Any] = []
    for column_name in dataframe.columns:
        aggregates.append(
            F.sum(F.when(F.col(column_name).isNull(), 1).otherwise(0)).alias(f"{column_name}_null_count")
        )
        aggregates.append(F.countDistinct(F.col(column_name)).alias(f"{column_name}_distinct_count"))

    row = dataframe.agg(*aggregates).collect()[0]
    result: dict[str, tuple[int, int]] = {}
    for column_name in dataframe.columns:
        null_count = row[f"{column_name}_null_count"]
        distinct_count = row[f"{column_name}_distinct_count"]
        result[column_name] = (int(null_count or 0), int(distinct_count or 0))
    return result


def _profile_numeric_metrics(dataframe: DataFrame) -> dict[str, dict[str, int | float | Decimal | None]]:
    """Compute min/max/mean for applicable numeric columns."""

    numeric_columns = _numeric_column_names(dataframe)
    if not numeric_columns:
        return {}

    metrics_aggregates: list[Any] = []
    for column_name in numeric_columns:
        metrics_aggregates.extend(
            [
                F.min(F.col(column_name)).alias(f"{column_name}_min"),
                F.max(F.col(column_name)).alias(f"{column_name}_max"),
                F.avg(F.col(column_name)).alias(f"{column_name}_avg"),
            ]
        )

    row = dataframe.agg(*metrics_aggregates).collect()[0]
    result: dict[str, dict[str, int | float | Decimal | None]] = {}
    for column_name in numeric_columns:
        result[column_name] = {
            "minimum": row[f"{column_name}_min"],
            "maximum": row[f"{column_name}_max"],
            "mean": row[f"{column_name}_avg"],
        }
    return result


def profile_dataframe(dataframe: DataFrame) -> DatasetProfile:
    """Inspect a PySpark DataFrame and return a structured dataset profile."""

    if dataframe is None:
        raise ValueError("DataFrame argument is required and cannot be None.")
    if not isinstance(dataframe, DataFrame):
        raise TypeError(f"Expected a PySpark DataFrame, received {type(dataframe).__name__}.")

    try:
        row_count = int(dataframe.count())
    except Exception as exc:
        raise RuntimeError("Failed to calculate dataset-level metrics for the provided PySpark DataFrame.") from exc

    try:
        column_count = len(dataframe.columns)
        exact_duplicate_row_count = _duplicate_row_count(dataframe, row_count=row_count)
    except Exception as exc:
        raise RuntimeError("Failed to calculate duplicate-row count for the provided PySpark DataFrame.") from exc

    try:
        column_profiles: list[ColumnProfile] = []
        column_null_and_distinct = _profile_column_aggregates(dataframe)
        numeric_metrics = _profile_numeric_metrics(dataframe)

        for column_name in dataframe.columns:
            field = next(field for field in dataframe.schema.fields if field.name == column_name)
            data_type = str(field.dataType)
            nullable = bool(field.nullable)
            null_count, distinct_count = column_null_and_distinct.get(column_name, (0, 0))
            null_percentage = (null_count / row_count) if row_count else 0.0

            metric_values = numeric_metrics.get(column_name, {})
            column_profiles.append(
                ColumnProfile(
                    column_name=column_name,
                    data_type=data_type,
                    nullable=nullable,
                    null_count=null_count,
                    null_percentage=float(null_percentage),
                    distinct_count=distinct_count,
                    minimum=metric_values.get("minimum"),
                    maximum=metric_values.get("maximum"),
                    mean=metric_values.get("mean"),
                )
            )

        return DatasetProfile(
            row_count=row_count,
            column_count=column_count,
            exact_duplicate_row_count=exact_duplicate_row_count,
            columns=column_profiles,
        )
    except Exception as exc:
        raise RuntimeError("Failed to calculate column statistics for the provided PySpark DataFrame.") from exc


__all__ = [
    "ColumnProfile",
    "DatasetProfile",
    "profile_dataframe",
]
