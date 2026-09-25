import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pyspark.sql import SparkSession

from backend.app.ingestion.parsers.excel import parse_excel
from backend.app.ingestion.spark_adapter import pandas_to_spark_dataframe


EXCEL_PATH = REPO_ROOT / "experiments" / "ingestion" / "data" / "sample_customers.xlsx"


def main():
    spark = (
        SparkSession.builder
        .master("spark://spark-master:7077")
        .appName("Excel to Spark Adapter Experiment")
        .config("spark.eventLog.enabled", "false")
        .getOrCreate()
    )

    try:
        pandas_df = parse_excel(str(EXCEL_PATH))

        print("Pandas DataFrame:")
        print(pandas_df)
        print("\nPandas dtypes:")
        print(pandas_df.dtypes)

        spark_df = pandas_to_spark_dataframe(spark, pandas_df)

        print("\nSpark DataFrame schema:")
        spark_df.printSchema()

        print("\nSpark DataFrame rows:")
        spark_df.show()
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
