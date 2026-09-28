import pathlib
import sys

from pyspark.sql import SparkSession

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.lakehouse.silver.profile import profile_dataframe


def main() -> None:
    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("test-silver-profile")
        .getOrCreate()
    )

    try:
        # 1) Normal small DataFrame
        df_normal = spark.createDataFrame(
            [(1, 20, "A"), (2, 30, "B"), (3, 40, "C")],
            ["id", "age", "name"],
        )
        normal_profile = profile_dataframe(df_normal)
        assert normal_profile.row_count == 3
        assert normal_profile.column_count == 3
        assert normal_profile.exact_duplicate_row_count == 0

        normal_columns = {column.column_name: column for column in normal_profile.columns}
        assert normal_columns["age"].minimum == 20
        assert normal_columns["age"].maximum == 40
        assert float(normal_columns["age"].mean) == 30.0
        assert normal_columns["name"].minimum is None
        assert normal_columns["name"].maximum is None
        assert normal_columns["name"].mean is None

        # 2) Empty DataFrame
        df_empty = spark.createDataFrame([], df_normal.schema)
        empty_profile = profile_dataframe(df_empty)
        assert empty_profile.row_count == 0
        assert empty_profile.exact_duplicate_row_count == 0

        # 3) Null-value DataFrame
        df_null = spark.createDataFrame(
            [(1, 20), (2, None), (3, 30)],
            ["id", "age"],
        )
        null_profile = profile_dataframe(df_null)
        null_columns = {column.column_name: column for column in null_profile.columns}
        assert null_columns["age"].null_count == 1
        assert abs(null_columns["age"].null_percentage - (1.0 / 3.0)) < 1e-9

        # 4) Exact duplicate rows
        df_dupes = spark.createDataFrame(
            [(1, "A"), (1, "A"), (2, "B")],
            ["id", "name"],
        )
        dupes_profile = profile_dataframe(df_dupes)
        assert dupes_profile.exact_duplicate_row_count == 1

        # 5) Invalid inputs
        try:
            profile_dataframe(None)
            raise AssertionError("Expected ValueError for None input.")
        except ValueError:
            pass

        try:
            profile_dataframe("hello")
            raise AssertionError("Expected TypeError for string input.")
        except TypeError:
            pass

        print("PASS: all 5 edge-case checks for profile_dataframe() passed.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
