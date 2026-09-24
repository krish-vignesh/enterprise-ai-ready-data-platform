from backend.app.spark.session import create_spark_session


def main():
    spark = create_spark_session()

    input_path = "s3a://ai-data/customers_large/customers_large.jsonl"

    print("Reading data from:", input_path)

    df = spark.read.json(input_path)

    print("Number of partitions:", df.rdd.getNumPartitions())

    print("Executing count action...")

    row_count = df.count()

    print("Row count:", row_count)

    print("Sample records:")

    df.show(5, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()