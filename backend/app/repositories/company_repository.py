"""Repository for Company persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company


class CompanyRepository:
    """Persistence operations for Company records."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, company_id: int) -> Company | None:
        """Fetch a company by its primary key."""
        return self.session.get(Company, company_id)

    def list_all(self) -> list[Company]:
        """Return all companies in the database."""
        return list(self.session.scalars(select(Company)).all())
