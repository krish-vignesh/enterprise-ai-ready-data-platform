from __future__ import annotations

from pyspark.sql import DataFrame


def clean_dataframe(dataframe: DataFrame) -> DataFrame:
    """Remove exact duplicate rows while preserving the original schema."""

    if dataframe is None:
        raise ValueError("DataFrame argument is required and cannot be None.")
    if not isinstance(dataframe, DataFrame):
        raise TypeError(f"Expected a PySpark DataFrame, received {type(dataframe).__name__}.")

    try:
        # A zero-column DataFrame has no duplicate row definition to compare, so it is
        # returned unchanged rather than risking a Spark operation that requires columns.
        if not dataframe.columns:
            return dataframe

        return dataframe.dropDuplicates()
    except Exception as exc:
        raise RuntimeError(
            "Failed to remove exact duplicate rows from the provided PySpark DataFrame."
        ) from exc


__all__ = ["clean_dataframe"]
