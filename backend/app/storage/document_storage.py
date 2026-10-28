
"""Store and verify original document files in MinIO."""

import asyncio
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID

from minio import Minio

from app.config.settings import settings


class StoredObjectVerificationError(RuntimeError):
    """Raised when a stored object does not match the expected metadata."""


@dataclass(frozen=True, slots=True)
class StoredObjectMetadata:
    """Describe a successfully verified MinIO object."""

    bucket_name: str
    object_key: str
    size_bytes: int
    etag: str | None


def build_document_object_key(
    dataset_id: UUID,
    document_id: UUID,
) -> str:
    """Build a deterministic object key for a document's original file."""
    return f"datasets/{dataset_id}/documents/{document_id}/original"


class MinioDocumentStorage:
    """Upload original files to MinIO and verify their stored metadata."""

    def __init__(
        self,
        client: Minio | None = None,
        bucket_name: str | None = None,
    ) -> None:
        """Initialize the adapter without making network requests."""
        self._client = client or Minio(
            endpoint=f"{settings.minio_host}:{settings.minio_port}",
            access_key=settings.minio_username,
            secret_key=settings.minio_password,
            secure=False,
        )
        self.bucket_name = bucket_name or settings.workspace_records_bucket

    async def upload_file(
        self,
        *,
        object_key: str,
        file_obj: BinaryIO,
        file_size_bytes: int,
        content_type: str | None,
    ) -> None:
        """Upload a seekable file stream without blocking the event loop."""
        if file_size_bytes < 0:
            raise ValueError("file_size_bytes cannot be negative")

        await asyncio.to_thread(
            self._upload_file_sync,
            object_key,
            file_obj,
            file_size_bytes,
            content_type or "application/octet-stream",
        )

    def _upload_file_sync(
        self,
        object_key: str,
        file_obj: BinaryIO,
        file_size_bytes: int,
        content_type: str,
    ) -> None:
        """Perform the blocking MinIO SDK upload."""
        file_obj.seek(0)

        self._client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            data=file_obj,
            length=file_size_bytes,
            content_type=content_type,
        )

    async def verify_object(
        self,
        *,
        object_key: str,
        expected_size_bytes: int,
    ) -> StoredObjectMetadata:
        """Verify that the object exists and has the expected size."""
        if expected_size_bytes < 0:
            raise ValueError("expected_size_bytes cannot be negative")

        stored_object = await asyncio.to_thread(
            self._client.stat_object,
            self.bucket_name,
            object_key,
        )

        if stored_object.size != expected_size_bytes:
            raise StoredObjectVerificationError(
                "Stored object size does not match the expected file size."
            )

        return StoredObjectMetadata(
            bucket_name=self.bucket_name,
            object_key=object_key,
            size_bytes=stored_object.size,
            etag=stored_object.etag,
        )
