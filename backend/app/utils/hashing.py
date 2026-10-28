"""Utilities for calculating file content hashes."""

from hashlib import sha256
from typing import BinaryIO


def calculate_sha256(
    file_obj: BinaryIO,
    *,
    chunk_size: int = 1024 * 1024,
) -> str:
    """Calculate a file's SHA-256 hash without loading it all into memory."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    original_position = file_obj.tell()

    try:
        file_obj.seek(0)
        digest = sha256()

        while chunk := file_obj.read(chunk_size):
            digest.update(chunk)

        return digest.hexdigest()

    finally:
        file_obj.seek(original_position)
