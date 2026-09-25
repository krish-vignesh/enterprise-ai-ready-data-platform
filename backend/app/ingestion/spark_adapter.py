from __future__ import annotations

from typing import Any

import pandas as pd


def pandas_to_spark_dataframe(spark: Any, data: pd.DataFrame):
    """Convert an existing pandas DataFrame into a Spark DataFrame."""
    return spark.createDataFrame(data)
