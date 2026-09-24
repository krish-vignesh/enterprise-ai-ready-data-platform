from pyspark.sql import SparkSession


def main():
    spark = (
        SparkSession.builder
        .appName("Spark Partition Experiment")
        .getOrCreate()
    )

    print("\n========== CONFIG CHECK VERSION 2 ==========")

    print("Max partition bytes:", spark.conf.get("spark.sql.files.maxPartitionBytes"))

    print("Open cost bytes:", spark.conf.get("spark.sql.files.openCostInBytes"))

    print("========== END CONFIG CHECK ==========")

    input_path = (
        "s3a://ai-data/"
        "spark_scaling_customers/"
        "spark_scaling_customers.jsonl"
    )

    print("Reading:", input_path)

    # Read the dataset from MinIO
    df = spark.read.json(input_path)

    # Check the natural partition count
    natural_partitions = df.rdd.getNumPartitions()

    print("Natural partitions:", natural_partitions)

    # Deliberately increase the partition count
    print("Repartitioning to 16 partitions...")

    df = df.repartition(16)

    repartitioned_partitions = df.rdd.getNumPartitions()

    print("Partitions after repartition:", repartitioned_partitions)

    # One action
    print("Running count()...")

    row_count = df.count()

    print("Row count:", row_count)

    # One action
    print("Running count()...")

    row_count = df.count()

    print("Row count:", row_count)

    print("========== EXPERIMENT COMPLETE ==========\n")

    spark.stop()


if __name__ == "__main__":
    main()

    print("========== EXPERIMENT COMPLETE ==========\n")

