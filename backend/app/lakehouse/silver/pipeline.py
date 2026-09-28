from __future__ import annotations

from dataclasses import dataclass

from pyspark.sql import SparkSession

from backend.app.lakehouse.bronze.delta import read_bronze_delta
from backend.app.lakehouse.silver.cleaning import clean_dataframe
from backend.app.lakehouse.silver.delta import WriteMode, write_silver_delta
from backend.app.lakehouse.silver.profile import DatasetProfile, profile_dataframe
from backend.app.lakehouse.silver.report import DatasetQualityReport, generate_quality_report


@dataclass(frozen=True)
class SilverPipelineResult:
    """Structured outcome for a Bronze-to-Silver Common Silver pipeline run."""

    dataset_name: str
    bronze_table_path: str
    silver_table_path: str
    input_row_count: int
    output_row_count: int
    duplicate_rows_removed: int
    quality_status: str
    profile: DatasetProfile
    report: DatasetQualityReport


def run_silver_pipeline(
    spark: SparkSession,
    bronze_table_path: str,
    silver_table_path: str,
    dataset_name: str | None = None,
    mode: WriteMode = "overwrite",
    partition_by: list[str] | None = None,
) -> SilverPipelineResult:
    """Run the common Bronze-to-Silver pipeline for a dataset-agnostic DataFrame."""

    if spark is None:
        raise ValueError("SparkSession argument is required and cannot be None.")
    if not isinstance(spark, SparkSession):
        raise TypeError(f"Expected a PySpark SparkSession, received {type(spark).__name__}.")

    if not isinstance(bronze_table_path, str) or not bronze_table_path.strip():
        raise ValueError("bronze_table_path is required and must be a non-empty string.")
    if not isinstance(silver_table_path, str) or not silver_table_path.strip():
        raise ValueError("silver_table_path is required and must be a non-empty string.")
    if dataset_name is not None and (not isinstance(dataset_name, str) or not dataset_name.strip()):
        raise ValueError("dataset_name must be a non-empty string when provided.")

    effective_dataset_name = dataset_name.strip() if dataset_name is not None else "unknown"

    try:
        bronze_df = read_bronze_delta(spark, bronze_table_path)
    except Exception as exc:
        raise RuntimeError("Failed to read Bronze Delta table for the Silver pipeline.") from exc

    try:
        profile = profile_dataframe(bronze_df)
    except Exception as exc:
        raise RuntimeError("Failed to profile the Bronze DataFrame for the Silver pipeline.") from exc

    try:
        report = generate_quality_report(profile)
    except Exception as exc:
        raise RuntimeError("Failed to generate the Silver quality report for the Bronze DataFrame.") from exc

    try:
        cleaned_df = clean_dataframe(bronze_df)
    except Exception as exc:
        raise RuntimeError("Failed to clean the Bronze DataFrame in the Silver pipeline.") from exc

    input_row_count = profile.row_count
    output_row_count = int(cleaned_df.count())
    duplicate_rows_removed = input_row_count - output_row_count

    try:
        write_silver_delta(cleaned_df, silver_table_path, mode=mode, partition_by=partition_by)
    except Exception as exc:
        raise RuntimeError("Failed to write the cleaned DataFrame to the Silver Delta table.") from exc

    return SilverPipelineResult(
        dataset_name=effective_dataset_name,
        bronze_table_path=bronze_table_path,
        silver_table_path=silver_table_path,
        input_row_count=input_row_count,
        output_row_count=output_row_count,
        duplicate_rows_removed=duplicate_rows_removed,
        quality_status=report.overall_status,
        profile=profile,
        report=report,
    )


__all__ = ["SilverPipelineResult", "run_silver_pipeline"]
