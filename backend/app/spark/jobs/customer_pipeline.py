from app.spark.io.reader import read_data
from app.spark.io.writer import write_data
from app.spark.session import create_spark_session
from app.spark.transformations.customer import transform_customer_data

INPUT_PATH = "s3a://ai-data/spark_scaling_customers/spark_scaling_customers.jsonl"
OUTPUT_PATH = "s3a://ai-data/processed/customers/"


def main():
    spark = create_spark_session()

    try:
        df = read_data(
            spark=spark,
            input_path=INPUT_PATH,
            input_format="jsonl",
        )

        transformed_df = transform_customer_data(df)

        write_data(
            df=transformed_df,
            output_path=OUTPUT_PATH,
            output_format="parquet",
            mode="overwrite",
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
