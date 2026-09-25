from pyspark.sql import SparkSession
import pandas as pd

from app.ingestion.spark_adapter import pandas_to_spark_dataframe


def main():
    spark = (
        SparkSession.builder
        .appName("Spark Adapter Test")
        .master("local[*]")
        .config("spark.eventLog.enabled", "false")
        .getOrCreate()
    )

    try:
        pandas_df = pd.DataFrame(
            {
                "customer_id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "purchase_amount": [2500, 4500, 7500],
            }
        )

        print("\n--- Pandas DataFrame ---")
        print(pandas_df)

        spark_df = pandas_to_spark_dataframe(
            spark=spark,
            data=pandas_df,
        )

        print("\n--- Spark DataFrame Schema ---")
        spark_df.printSchema()

        print("\n--- Spark DataFrame Data ---")
        spark_df.show()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()