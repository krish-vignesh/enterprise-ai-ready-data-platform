"""Repository for Dataset persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dataset import Dataset


class DatasetRepository:
    """Persistence operations for Dataset records."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, dataset_id: int) -> Dataset | None:
        """Fetch a dataset by its primary key."""
        return self.session.get(Dataset, dataset_id)

    def list_by_company(self, company_id: int) -> list[Dataset]:
        """Return all datasets for a company."""
        statement = select(Dataset).where(Dataset.company_id == company_id)
        return list(self.session.scalars(statement).all())
