"""Repository for User persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


logger = logging.getLogger(__name__)


class UserRepository:
    """Provide database access for User records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with the session owned by the caller."""
        self.session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        """Return a user by internal UUID, or None if not found."""
        try:
            user = await self.session.get(User, user_id)

            logger.debug(
                "repository.user.get_by_id completed user_id=%s found=%s",
                user_id,
                user is not None,
            )

            return user

        except Exception:
            logger.exception(
                "repository.user.get_by_id failed user_id=%s",
                user_id,
            )
            raise

    async def get_by_keycloak_subject(
        self,
        keycloak_subject: str,
    ) -> User | None:
        """Return a user by Keycloak subject, or None if not found."""
        statement = select(User).where(
            User.keycloak_subject == keycloak_subject,
        )

        try:
            result = await self.session.scalars(statement)
            user = result.one_or_none()

            logger.debug(
                "repository.user.get_by_keycloak_subject completed found=%s",
                user is not None,
            )

            return user

        except Exception:
            logger.exception(
                "repository.user.get_by_keycloak_subject failed",
            )
            raise

    def add(self, user: User) -> User:
        """Stage a user for persistence without committing."""
        try:
            self.session.add(user)

            logger.debug("repository.user.add staged")

            return user

        except Exception:
            logger.exception("repository.user.add failed")
            raise

    def update_profile(
        self,
        user: User,
        *,
        email: str | None,
        display_name: str | None,
    ) -> User:
        """Update the stored user profile snapshot."""
        try:
            user.email = email
            user.display_name = display_name

            logger.debug(
                "repository.user.update_profile staged user_id=%s",
                user.user_id,
            )

            return user

        except Exception:
            logger.exception(
                "repository.user.update_profile failed user_id=%s",
                user.user_id,
            )
            raise
