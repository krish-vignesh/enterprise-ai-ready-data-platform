"""Resolve and provision internal users from validated Keycloak identities."""

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)

USER_SUBJECT_UNIQUE_CONSTRAINT = "uq_users_keycloak_subject"


def _get_constraint_name(error: IntegrityError) -> str | None:
    """Return the database constraint name when the driver exposes it."""
    original_error = error.orig
    diagnostic = getattr(original_error, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)

    if isinstance(constraint_name, str):
        return constraint_name

    return None


class IdentityService:
    """Resolve or provision an internal User for a validated identity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with the caller-provided session."""
        self.session = session
        self.user_repository = UserRepository(session)

    async def resolve_or_provision_user(
        self,
        *,
        keycloak_subject: str,
        email: str | None,
        display_name: str | None,
    ) -> User:
        """Resolve an existing user or provision one on first login."""
        try:
            async with self.session.begin():
                user = await self.user_repository.get_by_keycloak_subject(
                    keycloak_subject
                )

                if user is not None:
                    profile_updated = self._synchronize_profile(
                        user,
                        email=email,
                        display_name=display_name,
                    )
                    user_was_created = False

                else:
                    user = User(
                        keycloak_subject=keycloak_subject,
                        email=email,
                        display_name=display_name,
                    )
                    self.user_repository.add(user)

                    # Generate the UUID and execute the INSERT inside
                    # the current transaction.
                    await self.session.flush()

                    profile_updated = False
                    user_was_created = True

            # The transaction has successfully committed at this point.
            if user_was_created:
                logger.info(
                    "identity.user.provisioned user_id=%s",
                    user.user_id,
                )

            elif profile_updated:
                logger.info(
                    "identity.user.profile_updated user_id=%s",
                    user.user_id,
                )

            else:
                logger.info(
                    "identity.user.resolved user_id=%s",
                    user.user_id,
                )

            return user

        except IntegrityError as error:
            if _get_constraint_name(error) != USER_SUBJECT_UNIQUE_CONSTRAINT:
                logger.exception(
                    "identity.user.provisioning_failed reason=integrity_error"
                )
                raise

            logger.info("identity.user.concurrent_provisioning_detected")

            # The failed transaction has already been rolled back
            # by the session.begin() context manager.
            try:
                async with self.session.begin():
                    user = await self.user_repository.get_by_keycloak_subject(
                        keycloak_subject
                    )

                    if user is not None:
                        profile_updated = self._synchronize_profile(
                            user,
                            email=email,
                            display_name=display_name,
                        )

                if user is None:
                    raise

                logger.info(
                    "identity.user.concurrent_provisioning_recovered user_id=%s",
                    user.user_id,
                )

                if profile_updated:
                    logger.info(
                        "identity.user.profile_updated user_id=%s",
                        user.user_id,
                    )

                return user

            except Exception:
                logger.exception("identity.user.concurrent_recovery_failed")
                raise

        except Exception:
            logger.exception("identity.user.provisioning_failed")
            raise

    def _synchronize_profile(
        self,
        user: User,
        *,
        email: str | None,
        display_name: str | None,
    ) -> bool:
        """Synchronize supplied profile claims while preserving absent ones."""
        updated_email = email if email is not None else user.email
        updated_display_name = (
            display_name if display_name is not None else user.display_name
        )

        if updated_email == user.email and updated_display_name == user.display_name:
            return False

        self.user_repository.update_profile(
            user,
            email=updated_email,
            display_name=updated_display_name,
        )

        return True
