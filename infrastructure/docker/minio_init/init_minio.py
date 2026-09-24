import os
import time

from minio import Minio
from minio.error import S3Error


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ["MINIO_USERNAME"]
MINIO_SECRET_KEY = os.environ["MINIO_PASSWORD"]

BUCKET_NAME = "spark-events"

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
            if client.bucket_exists(BUCKET_NAME):
                print(f"Bucket '{BUCKET_NAME}' already exists.")
                return

            client.make_bucket(BUCKET_NAME)
            print(f"Bucket '{BUCKET_NAME}' created successfully.")
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