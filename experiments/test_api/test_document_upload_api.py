
"""API tests for single-document uploads."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import hashlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.documents import router
from app.db.dependencies import get_db
from app.middleware.request_id import RequestIDMiddleware
from app.models.enums import DocumentStatus
from app.services.document_upload_workflow import DocumentUploadOutcome
import app.api.documents as documents_api


@pytest.fixture
def test_client():
    """Create an isolated FastAPI application for API tests."""
    app = FastAPI()

    app.add_middleware(RequestIDMiddleware)
    app.include_router(router)

    session = MagicMock(spec=AsyncSession)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client, session

    app.dependency_overrides.clear()


def test_successful_single_document_upload(test_client, monkeypatch):
    """A valid document upload should return HTTP 201."""
    client, session = test_client

    dataset_id = uuid4()
    document_id = uuid4()
    upload_attempt_id = uuid4()

    file_content = b"sales,amount\nJanuary,100\n"

    document = SimpleNamespace(
        document_id=document_id,
        dataset_id=dataset_id,
        original_filename="sales.csv",
        detected_format="csv",
        content_type="text/csv",
        file_size_bytes=len(file_content),
        sha256=hashlib.sha256(file_content).hexdigest(),
        status=DocumentStatus.AVAILABLE,
    )

    upload_attempt = SimpleNamespace(
        upload_attempt_id=upload_attempt_id,
    )

    workflow_result = SimpleNamespace(
        outcome=DocumentUploadOutcome.UPLOADED,
        document=document,
        upload_attempt=upload_attempt,
    )

    workflow_mock = AsyncMock(return_value=workflow_result)

    monkeypatch.setattr(
        documents_api,
        "upload_document",
        workflow_mock,
    )

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={
            "file": (
                "sales.csv",
                file_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["outcome"] == "UPLOADED"
    assert response_data["document"]["document_id"] == str(document_id)
    assert response_data["document"]["dataset_id"] == str(dataset_id)
    assert response_data["document"]["original_filename"] == "sales.csv"
    assert response_data["upload_attempt_id"] == str(upload_attempt_id)

    request_id = response.headers["x-request-id"]
    assert len(request_id) == 36

    workflow_mock.assert_awaited_once()

    workflow_arguments = workflow_mock.await_args

    assert workflow_arguments.args[0] is session
    assert workflow_arguments.kwargs["dataset_id"] == dataset_id
    assert workflow_arguments.kwargs["filename"] == "sales.csv"
    assert workflow_arguments.kwargs["detected_format"] == "csv"
    assert workflow_arguments.kwargs["content_type"] == "text/csv"
    assert workflow_arguments.kwargs["file_size_bytes"] == len(file_content)
    assert workflow_arguments.kwargs["sha256"] == hashlib.sha256(
        file_content
    ).hexdigest()
    assert workflow_arguments.kwargs["request_id"] == request_id



def test_already_available_document_returns_200(test_client, monkeypatch):
    """An existing available document should return HTTP 200."""
    client, session = test_client

    dataset_id = uuid4()
    document_id = uuid4()

    file_content = b"sales,amount\nJanuary,100\n"

    document = SimpleNamespace(
        document_id=document_id,
        dataset_id=dataset_id,
        original_filename="sales.csv",
        detected_format="csv",
        content_type="text/csv",
        file_size_bytes=len(file_content),
        sha256=hashlib.sha256(file_content).hexdigest(),
        status=DocumentStatus.AVAILABLE,
    )

    workflow_result = SimpleNamespace(
        outcome=DocumentUploadOutcome.ALREADY_AVAILABLE,
        document=document,
        upload_attempt=None,
    )

    workflow_mock = AsyncMock(return_value=workflow_result)

    monkeypatch.setattr(
        documents_api,
        "upload_document",
        workflow_mock,
    )

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={
            "file": (
                "sales.csv",
                file_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["outcome"] == "ALREADY_AVAILABLE"
    assert response_data["document"]["document_id"] == str(document_id)
    assert response_data["upload_attempt_id"] is None

    workflow_mock.assert_awaited_once()


def test_upload_in_progress_returns_409(test_client, monkeypatch):
    """An upload already in progress should return HTTP 409."""
    client, _ = test_client

    dataset_id = uuid4()
    document_id = uuid4()
    attempt_id = uuid4()
    file_content = b"sales,amount\nJanuary,100\n"

    document = SimpleNamespace(
        document_id=document_id,
        dataset_id=dataset_id,
        original_filename="sales.csv",
        detected_format="csv",
        content_type="text/csv",
        file_size_bytes=len(file_content),
        sha256=hashlib.sha256(file_content).hexdigest(),
        status=DocumentStatus.AVAILABLE,
    )

    workflow_result = SimpleNamespace(
        outcome=DocumentUploadOutcome.UPLOAD_IN_PROGRESS,
        document=document,
        upload_attempt=SimpleNamespace(upload_attempt_id=attempt_id),
    )

    workflow_mock = AsyncMock(return_value=workflow_result)
    monkeypatch.setattr(documents_api, "upload_document", workflow_mock)

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={"file": ("sales.csv", file_content, "text/csv")},
    )

    assert response.status_code == 409
    assert response.json()["outcome"] == "UPLOAD_IN_PROGRESS"
    assert response.json()["upload_attempt_id"] == str(attempt_id)
    workflow_mock.assert_awaited_once()


def test_dataset_not_found_returns_404(test_client, monkeypatch):
    """A missing dataset should return HTTP 404."""
    client, _ = test_client
    dataset_id = uuid4()

    workflow_mock = AsyncMock(
        side_effect=documents_api.DatasetNotFoundError("Dataset not found")
    )
    monkeypatch.setattr(documents_api, "upload_document", workflow_mock)

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={"file": ("sales.csv", b"sales,amount\nJanuary,100\n", "text/csv")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found."
    workflow_mock.assert_awaited_once()


def test_uncertain_storage_outcome_returns_503(test_client, monkeypatch):
    """An uncertain storage outcome should return HTTP 503."""
    client, _ = test_client
    dataset_id = uuid4()

    workflow_mock = AsyncMock(
        side_effect=documents_api.DocumentUploadOutcomeUncertainError(
            "Storage outcome uncertain"
        )
    )
    monkeypatch.setattr(documents_api, "upload_document", workflow_mock)

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={"file": ("sales.csv", b"sales,amount\nJanuary,100\n", "text/csv")},
    )

    assert response.status_code == 503
    assert "Do not blindly retry" in response.json()["detail"]
    workflow_mock.assert_awaited_once()


def test_finalization_failure_returns_500(test_client, monkeypatch):
    """A failed upload finalization should return HTTP 500."""
    client, _ = test_client
    dataset_id = uuid4()

    workflow_mock = AsyncMock(
        side_effect=documents_api.DocumentUploadFinalizationError(
            "Finalization failed"
        )
    )
    monkeypatch.setattr(documents_api, "upload_document", workflow_mock)

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={"file": ("sales.csv", b"sales,amount\nJanuary,100\n", "text/csv")},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "The document upload could not be safely finalized."
    )
    workflow_mock.assert_awaited_once()


@pytest.mark.parametrize(
    ("filename", "content", "expected_status"),
    [
        ("sales.exe", b"invalid file", 422),
        ("", b"invalid file", 422),
        ("sales.csv", b"", 422),
    ],
)
def test_invalid_document_uploads(
    test_client,
    monkeypatch,
    filename,
    content,
    expected_status,
):
    """Invalid uploads should fail before the workflow is called."""
    client, _ = test_client
    dataset_id = uuid4()

    workflow_mock = AsyncMock()
    monkeypatch.setattr(documents_api, "upload_document", workflow_mock)

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={"file": (filename, content, "application/octet-stream")},
    )

    assert response.status_code == expected_status
    workflow_mock.assert_not_awaited()


def test_oversized_document_returns_413(test_client, monkeypatch):
    """A document exceeding the configured limit should return HTTP 413."""
    client, _ = test_client
    dataset_id = uuid4()

    workflow_mock = AsyncMock()
    monkeypatch.setattr(documents_api, "upload_document", workflow_mock)
    monkeypatch.setattr(
        documents_api.settings,
        "max_upload_file_size_bytes",
        5,
    )

    response = client.post(
        f"/api/v1/datasets/{dataset_id}/documents",
        files={"file": ("sales.csv", b"123456", "text/csv")},
    )

    assert response.status_code == 413
    workflow_mock.assert_not_awaited()

