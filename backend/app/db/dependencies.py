"""FastAPI dependencies for database session management."""

from collections.abc import AsyncIterator
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Provide a request-scoped asynchronous database session."""
    session = AsyncSessionLocal()

    try:
        yield session
    except Exception:
        try:
            await session.rollback()
        except Exception:
            logger.exception("database.session.rollback_failed")
        raise
    finally:
        await session.close()
