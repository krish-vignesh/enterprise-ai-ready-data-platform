"""Repository for UploadAttempt persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.upload_attempt import UploadAttempt


class UploadAttemptRepository:
    """Persistence operations for UploadAttempt records."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, upload_attempt_id: int) -> UploadAttempt | None:
        """Fetch an upload attempt by its primary key."""
        return self.session.get(UploadAttempt, upload_attempt_id)

    def list_by_company(self, company_id: int) -> list[UploadAttempt]:
        """Return all upload attempts for a company."""
        statement = select(UploadAttempt).where(UploadAttempt.company_id == company_id)
        return list(self.session.scalars(statement).all())
