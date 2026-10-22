
"""Tests for the file hashing utility."""

from io import BytesIO

import pytest

from app.utils.hashing import calculate_sha256


def test_identical_content_produces_identical_hashes() -> None:
    first = BytesIO(b"enterprise-data")
    second = BytesIO(b"enterprise-data")

    assert calculate_sha256(first) == calculate_sha256(second)


def test_different_content_produces_different_hashes() -> None:
    first = BytesIO(b"enterprise-data")
    second = BytesIO(b"different-data")

    assert calculate_sha256(first) != calculate_sha256(second)


def test_original_file_position_is_preserved() -> None:
    file_obj = BytesIO(b"enterprise-data")
    file_obj.seek(4)

    calculate_sha256(file_obj)

    assert file_obj.tell() == 4


def test_invalid_chunk_size_is_rejected() -> None:
    with pytest.raises(ValueError, match="chunk_size"):
        calculate_sha256(BytesIO(b"data"), chunk_size=0)
