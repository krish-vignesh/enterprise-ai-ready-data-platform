"""Integration tests for FastAPI database dependency lifecycle."""

from unittest.mock import MagicMock, patch

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.dependencies import get_db


app = FastAPI()


@app.get("/test-db")
def db_test_endpoint(db: Session = Depends(get_db)) -> dict[str, str]:
    """A minimal endpoint that receives a database session."""
    return {"status": "session received"}


def test_fastapi_closes_db_session_after_request() -> None:
    """FastAPI should close the yielded session after the request."""
    mock_session = MagicMock(spec=Session)

    with patch(
        "app.db.dependencies.SessionLocal",
        return_value=mock_session,
    ):
        with TestClient(app) as client:
            response = client.get("/test-db")

    assert response.status_code == 200
    assert response.json() == {"status": "session received"}
    mock_session.close.assert_called_once()
