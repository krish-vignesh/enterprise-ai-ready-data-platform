"""Integration tests for FastAPI database dependency lifecycle."""

from unittest.mock import AsyncMock, patch

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db


app = FastAPI()


@app.get("/test-db")
async def db_test_endpoint(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """A minimal endpoint that receives an asynchronous database session."""
    return {"status": "session received"}


def test_fastapi_closes_db_session_after_request() -> None:
    """FastAPI should close the asynchronous session after the request."""
    mock_session = AsyncMock(spec=AsyncSession)

    with patch(
        "app.db.dependencies.AsyncSessionLocal",
        return_value=mock_session,
    ):
        with TestClient(app) as client:
            response = client.get("/test-db")

    assert response.status_code == 200
    assert response.json() == {"status": "session received"}

    mock_session.close.assert_awaited_once()
    mock_session.rollback.assert_not_awaited()
