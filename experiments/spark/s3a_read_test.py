from pyspark.sql import SparkSession
import time


def main():
    spark = (
        SparkSession.builder
        .appName("Spark Partition Experiment")
        .getOrCreate()
    )

    input_path = (
        "s3a://ai-data/"
        "spark_scaling_customers/"
        "spark_scaling_customers.jsonl"
    )

    print("\n========== SPARK PARTITION EXPERIMENT ==========")
    print("Max partition bytes:", spark.conf.get("spark.sql.files.maxPartitionBytes"))
    print("Open cost bytes:", spark.conf.get("spark.sql.files.openCostInBytes"))
    print("Reading:", input_path)

    # Read the dataset from MinIO
    df = spark.read.json(input_path)

    # Check the natural partition count
    natural_partitions = df.rdd.getNumPartitions()

    print("Natural partitions:", natural_partitions)

    print("Repartitioning to 16 partitions...")

    df = df.repartition(16)

    repartitioned_partitions = df.rdd.getNumPartitions()

    print("Partitions after repartition:", repartitioned_partitions)

    print("\n========== SPARK EXPLAIN PLAN ==========")

    df.explain(True)

    print("========== END EXPLAIN PLAN ==========\n")

    print("Running count()...")

    row_count = df.count()

    print("Row count:", row_count)

    print("========== EXPERIMENT COMPLETE ==========")
    print("Spark job finished.")
    print("Keeping Spark application alive for UI inspection.")
    print("Open http://localhost:4040 to inspect the Spark UI.")
    print("Stop the environment with: docker compose down")

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
