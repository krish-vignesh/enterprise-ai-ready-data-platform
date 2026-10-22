"""Repository for SourceSystem persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source_system import SourceSystem


class SourceSystemRepository:
    """Persistence operations for SourceSystem records."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, source_system_id: int) -> SourceSystem | None:
        """Fetch a source system by its primary key."""
        return self.session.get(SourceSystem, source_system_id)

    def list_by_company(self, company_id: int) -> list[SourceSystem]:
        """Return all source systems for a company."""
        statement = select(SourceSystem).where(SourceSystem.company_id == company_id)
        return list(self.session.scalars(statement).all())
