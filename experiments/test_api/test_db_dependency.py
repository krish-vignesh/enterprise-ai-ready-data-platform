
"""Tests for the backend database session dependency."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.dependencies import get_db


def test_get_db_yields_session_and_closes_it() -> None:
    """The dependency should yield a session and close it afterward."""
    mock_session = MagicMock()

    with patch(
        "app.db.dependencies.SessionLocal",
        return_value=mock_session,
    ):
        dependency = get_db()

        # Step 1: FastAPI receives the database session.
        yielded_session = next(dependency)
        assert yielded_session is mock_session

        # Step 2: Finishing the dependency must trigger cleanup.
        with pytest.raises(StopIteration):
            next(dependency)

    mock_session.close.assert_called_once()


def test_get_db_closes_session_after_exception() -> None:
    """The dependency should close the session even if an error occurs."""
    mock_session = MagicMock()

    with patch(
        "app.db.dependencies.SessionLocal",
        return_value=mock_session,
    ):
        dependency = get_db()

        # Start the dependency and receive the session.
        yielded_session = next(dependency)
        assert yielded_session is mock_session

        # Simulate an exception inside the code using the session.
        with pytest.raises(RuntimeError, match="Simulated failure"):
            dependency.throw(RuntimeError("Simulated failure"))

    # Cleanup must still happen when an exception is raised.
    mock_session.close.assert_called_once()