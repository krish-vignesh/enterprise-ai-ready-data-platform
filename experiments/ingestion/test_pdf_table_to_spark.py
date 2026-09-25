import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pyspark.sql import SparkSession

from backend.app.ingestion.parsers.pdf_tables import extract_pdf_tables
from backend.app.ingestion.spark_adapter import pandas_to_spark_dataframe


PDF_PATH = REPO_ROOT / "experiments" / "ingestion" / "data" / "sample_customers.pdf"


def main():
    spark = (
        SparkSession.builder
        .master("spark://spark-master:7077")
        .appName("PDF Table to Spark Adapter Experiment")
        .config("spark.eventLog.enabled", "false")
        .getOrCreate()
    )

    try:
        tables = extract_pdf_tables(str(PDF_PATH), pages="all", flavor="lattice")
        print(f"Extracted tables: {len(tables)}")

        if not tables:
            raise RuntimeError(
                f"No tables were extracted from PDF: {PDF_PATH}. "
                "Verify the fixture has lattice-detectable table borders."
            )

        for index, pandas_df in enumerate(tables, start=1):
            print(f"\nTable {index} (pandas DataFrame):")
            print(pandas_df)
            print("\nPandas dtypes:")
            print(pandas_df.dtypes)

            spark_df = pandas_to_spark_dataframe(spark, pandas_df)
            print(f"\nTable {index} Spark schema:")
            spark_df.printSchema()
            print(f"\nTable {index} Spark rows:")
            spark_df.show()
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
