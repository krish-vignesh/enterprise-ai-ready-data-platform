"""Validation rules for document uploads."""

from pathlib import PurePath


DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES = 50 * 1024 * 1024

ALLOWED_DOCUMENT_EXTENSIONS = frozenset(
    {
        ".pdf",
        ".docx",
        ".xlsx",
        ".csv",
        ".md",
        ".txt",
        ".json",
    }
)

MAX_FILENAME_LENGTH = 512


class DocumentUploadValidationError(ValueError):
    """Base exception for document-upload validation failures."""


class InvalidDocumentFilenameError(DocumentUploadValidationError):
    """Raised when an uploaded filename is invalid."""


class UnsupportedDocumentFormatError(DocumentUploadValidationError):
    """Raised when a document has an unsupported extension."""


class InvalidDocumentSizeError(DocumentUploadValidationError):
    """Raised when the supplied file size is invalid."""


class DocumentTooLargeError(DocumentUploadValidationError):
    """Raised when a document exceeds the configured size limit."""


def validate_document_upload_metadata(
    filename: str | None,
    file_size_bytes: int,
    *,
    max_file_size_bytes: int = DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES,
) -> None:
    """Validate filename, extension, and measured file size.

    This function does not read the file, inspect its contents,
    calculate its hash, or perform storage operations.
    """
    if not isinstance(filename, str) or not filename.strip():
        raise InvalidDocumentFilenameError("A non-empty filename is required.")

    if len(filename) > MAX_FILENAME_LENGTH:
        raise InvalidDocumentFilenameError(
            f"Filename cannot exceed {MAX_FILENAME_LENGTH} characters."
        )

    if (
        filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or any(ord(character) < 32 or ord(character) == 127 for character in filename)
    ):
        raise InvalidDocumentFilenameError(
            "Filename contains invalid path characters or control characters."
        )

    extension = PurePath(filename).suffix.lower()

    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise UnsupportedDocumentFormatError(
            f"Unsupported document extension: {extension or '(none)'}."
        )

    if (
        isinstance(file_size_bytes, bool)
        or not isinstance(file_size_bytes, int)
        or file_size_bytes < 0
    ):
        raise InvalidDocumentSizeError("File size must be a non-negative integer.")

    if (
        isinstance(max_file_size_bytes, bool)
        or not isinstance(max_file_size_bytes, int)
        or max_file_size_bytes <= 0
    ):
        raise ValueError("Maximum file size must be a positive integer.")

    if file_size_bytes > max_file_size_bytes:
        raise DocumentTooLargeError(
            f"File exceeds the maximum allowed size of {max_file_size_bytes} bytes."
        )
