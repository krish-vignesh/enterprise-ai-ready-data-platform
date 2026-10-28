import pytest

from app.validation.document_upload import (
    DocumentTooLargeError,
    InvalidDocumentFilenameError,
    InvalidDocumentSizeError,
    UnsupportedDocumentFormatError,
    validate_document_upload_metadata,
)


@pytest.mark.parametrize(
    "filename",
    [
        "report.pdf",
        "report.docx",
        "report.xlsx",
        "report.csv",
        "report.md",
        "report.txt",
        "report.json",
        "REPORT.PDF",
    ],
)
def test_supported_filename_is_accepted(filename: str) -> None:
    validate_document_upload_metadata(filename, 100)


@pytest.mark.parametrize(
    "filename",
    [
        None,
        "",
        "   ",
        "../report.pdf",
        r"..\report.pdf",
        "folder/report.pdf",
        "report.exe",
        "report",
        ".",
        "..",
        "report.pdf\x00",
    ],
)
def test_invalid_filename_or_extension_is_rejected(
    filename: str | None,
) -> None:
    with pytest.raises(
        (
            InvalidDocumentFilenameError,
            UnsupportedDocumentFormatError,
        )
    ):
        validate_document_upload_metadata(filename, 100)


def test_filename_over_maximum_length_is_rejected() -> None:
    filename = f"{'a' * 509}.pdf"

    with pytest.raises(InvalidDocumentFilenameError):
        validate_document_upload_metadata(filename, 100)


def test_file_exactly_at_limit_is_accepted() -> None:
    validate_document_upload_metadata(
        "report.csv",
        100,
        max_file_size_bytes=100,
    )


def test_file_over_limit_is_rejected() -> None:
    with pytest.raises(DocumentTooLargeError):
        validate_document_upload_metadata(
            "report.csv",
            101,
            max_file_size_bytes=100,
        )


def test_zero_byte_file_is_allowed_by_metadata_validation() -> None:
    validate_document_upload_metadata("empty.txt", 0)


@pytest.mark.parametrize("size", [-1, 1.5, True])
def test_invalid_file_size_is_rejected(size: object) -> None:
    with pytest.raises(InvalidDocumentSizeError):
        validate_document_upload_metadata(
            "report.csv",
            size,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("limit", [0, -1, True])
def test_invalid_configured_limit_is_rejected(limit: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        validate_document_upload_metadata(
            "report.csv",
            100,
            max_file_size_bytes=limit,  # type: ignore[arg-type]
        )
