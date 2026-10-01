import os
import time

from minio import Minio
from minio.error import S3Error


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ["MINIO_USERNAME"]
MINIO_SECRET_KEY = os.environ["MINIO_PASSWORD"]

AI_DATA_BUCKET_NAME = "ai-data"
SPARK_EVENTS_BUCKET_NAME = "spark-events"
WORKSPACE_RECORDS_BUCKET_NAME = os.getenv(
    "WORKSPACE_RECORDS_BUCKET",
    "workspace-records",
)

MAX_RETRIES = 30
RETRY_DELAY_SECONDS = 2


def create_bucket() -> None:
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            for bucket_name in (
                AI_DATA_BUCKET_NAME,
                SPARK_EVENTS_BUCKET_NAME,
                WORKSPACE_RECORDS_BUCKET_NAME,
            ):
                if client.bucket_exists(bucket_name):
                    print(f"Bucket '{bucket_name}' already exists.")
                    continue

                client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully.")
            return

        except Exception as exc:
            print(
                f"MinIO not ready "
                f"(attempt {attempt}/{MAX_RETRIES}): {exc}"
            )

            if attempt == MAX_RETRIES:
                raise

            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    create_bucket()