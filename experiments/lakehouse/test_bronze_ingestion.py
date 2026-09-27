from __future__ import annotations

import hashlib

from app.lakehouse.bronze.delta import read_bronze_delta
from app.lakehouse.bronze.pipeline import run_bronze_ingestion
from app.lakehouse.bronze.source import SourceArtifact
from app.spark.session import create_spark_session
from app.storage.minio_client import client

SOURCE_BUCKET = "ai-data"
SOURCE_OBJECT = "spark_scaling_customers/spark_scaling_customers.jsonl"
SOURCE_PATH = f"s3a://{SOURCE_BUCKET}/{SOURCE_OBJECT}"
BRONZE_TABLE_PATH = "s3a://ai-data/bronze/tables/spark_scaling_customers/"


def fetch_object_metadata(bucket_name: str, object_name: str) -> tuple[int, str]:
    """Read the actual source object from MinIO and compute its size and SHA-256 hash."""
    response = client.get_object(bucket_name, object_name)
    try:
        digest = hashlib.sha256()
        size = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        return size, digest.hexdigest()
    finally:
        response.close()


def delta_log_exists(spark, table_path: str) -> bool:
    """Check whether the Delta transaction log directory exists at the target S3A path."""
    table_uri = spark._jvm.java.net.URI.create(table_path.rstrip("/"))
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(table_uri, spark._jsc.hadoopConfiguration())
    delta_log_path = spark._jvm.org.apache.hadoop.fs.Path(f"{table_path.rstrip('/')}/_delta_log")
    return bool(fs.exists(delta_log_path))


def main() -> None:
    spark = create_spark_session()
    checks: dict[str, bool] = {
        "Spark session": False,
        "MinIO source read": False,
        "Bronze ingestion": False,
        "Delta read-back": False,
        "row-count consistency": False,
        "_delta_log existence": False,
    }

    try:
        print("=== Bronze integration test ===")
        print(f"Source object: {SOURCE_PATH}")
        print(f"Bronze table: {BRONZE_TABLE_PATH}")

        file_size, file_hash = fetch_object_metadata(SOURCE_BUCKET, SOURCE_OBJECT)
        print(f"Source file size: {file_size} bytes")
        print(f"Source SHA-256: {file_hash}")
        checks["MinIO source read"] = True

        source_artifact = SourceArtifact(
            company_id="test-company-001",
            company_name="Bronze Test Company",
            source_id="minio-test",
            source_object_path=SOURCE_PATH,
        )

        result = run_bronze_ingestion(
            spark=spark,
            source_artifact=source_artifact,
            dataset_name="spark_scaling_customers",
            source="minio-test",
            source_format="jsonl",
            source_object_path=SOURCE_PATH,
            source_file_name="spark_scaling_customers.jsonl",
            file_size=file_size,
            file_hash=file_hash,
            schema_version="v1",
            bronze_table_path=BRONZE_TABLE_PATH,
            mode="overwrite",
        )

        print("Bronze ingestion result:")
        print(result)
        checks["Bronze ingestion"] = result.get("status") == "success"
        checks["Spark session"] = spark is not None

        bronze_df = read_bronze_delta(spark, BRONZE_TABLE_PATH)
        read_row_count = bronze_df.count()
        print(f"Read-back row count: {read_row_count}")
        print("Schema:")
        bronze_df.printSchema()
        print("Sample rows:")
        bronze_df.show(5, truncate=False)

        checks["Delta read-back"] = read_row_count > 0 and len(bronze_df.schema.fields) > 0
        checks["row-count consistency"] = (result.get("record_count") == read_row_count) and read_row_count > 0
        checks["_delta_log existence"] = delta_log_exists(spark, BRONZE_TABLE_PATH)

        print("=== PASS/FAIL summary ===")
        for name, ok in checks.items():
            print(f"{name}: {'PASS' if ok else 'FAIL'}")

        if not all(checks.values()):
            failures = [name for name, ok in checks.items() if not ok]
            raise RuntimeError(f"Bronze integration test failed for: {', '.join(failures)}")

        print("PASS: Bronze integration test succeeded.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
