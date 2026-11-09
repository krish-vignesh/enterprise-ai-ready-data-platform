"""Tests for the backend database session dependency."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db


@pytest.mark.asyncio
async def test_get_db_yields_session_and_closes_it() -> None:
    """The dependency should yield an async session and close it afterward."""
    mock_session = AsyncMock(spec=AsyncSession)

    with patch(
        "app.db.dependencies.AsyncSessionLocal",
        return_value=mock_session,
    ):
        dependency = get_db()

        # Step 1: FastAPI receives the database session.
        yielded_session = await anext(dependency)
        assert yielded_session is mock_session

        # Step 2: Finishing the dependency triggers cleanup.
        with pytest.raises(StopAsyncIteration):
            await anext(dependency)

    mock_session.close.assert_awaited_once()
    mock_session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_db_rolls_back_and_closes_session_after_exception() -> None:
    """The dependency should roll back and close the session after an error."""
    mock_session = AsyncMock(spec=AsyncSession)

    with patch(
        "app.db.dependencies.AsyncSessionLocal",
        return_value=mock_session,
    ):
        dependency = get_db()

        yielded_session = await anext(dependency)
        assert yielded_session is mock_session

        with pytest.raises(RuntimeError, match="Simulated failure"):
            await dependency.athrow(RuntimeError("Simulated failure"))

    mock_session.rollback.assert_awaited_once()
    mock_session.close.assert_awaited_once()