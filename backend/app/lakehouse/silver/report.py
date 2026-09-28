from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.lakehouse.silver.profile import ColumnProfile, DatasetProfile


@dataclass(frozen=True)
class ColumnQualityReport:
    """Simple quality summary for one dataset column."""

    column_name: str
    null_count: int
    null_percentage: float
    distinct_count: int
    minimum: int | float | None = None
    maximum: int | float | None = None
    mean: float | None = None


@dataclass(frozen=True)
class DatasetQualityReport:
    """Dataset-level quality summary derived from a DatasetProfile."""

    row_count: int
    column_count: int
    exact_duplicate_row_count: int
    columns: list[ColumnQualityReport] = field(default_factory=list)
    overall_status: str = "PASS"


def _column_quality_report(column_profile: ColumnProfile) -> ColumnQualityReport:
    """Reuse existing profile values without recalculating anything."""

    return ColumnQualityReport(
        column_name=column_profile.column_name,
        null_count=column_profile.null_count,
        null_percentage=float(column_profile.null_percentage),
        distinct_count=column_profile.distinct_count,
        minimum=column_profile.minimum,
        maximum=column_profile.maximum,
        mean=column_profile.mean,
    )


def generate_quality_report(profile: DatasetProfile) -> DatasetQualityReport:
    """Convert an existing DatasetProfile into a structured quality report."""

    if profile is None:
        raise ValueError("DatasetProfile argument is required and cannot be None.")
    if not isinstance(profile, DatasetProfile):
        raise TypeError(f"Expected a DatasetProfile, received {type(profile).__name__}.")

    columns = [_column_quality_report(column_profile) for column_profile in profile.columns]

    if profile.exact_duplicate_row_count > 0 or any(column.null_count > 0 for column in profile.columns):
        overall_status = "REVIEW"
    else:
        overall_status = "PASS"

    return DatasetQualityReport(
        row_count=profile.row_count,
        column_count=profile.column_count,
        exact_duplicate_row_count=profile.exact_duplicate_row_count,
        columns=columns,
        overall_status=overall_status,
    )


__all__ = [
    "ColumnQualityReport",
    "DatasetQualityReport",
    "generate_quality_report",
]
