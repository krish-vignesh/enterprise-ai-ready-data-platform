"""Repository for StorageObject persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.storage_object import StorageObject


class StorageObjectRepository:
    """Persistence operations for StorageObject records."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, storage_object_id: int) -> StorageObject | None:
        """Fetch a storage object by its primary key."""
        return self.session.get(StorageObject, storage_object_id)

    def list_by_company(self, company_id: int) -> list[StorageObject]:
        """Return all storage objects associated with a company."""
        statement = select(StorageObject).where(StorageObject.company_id == company_id)
        return list(self.session.scalars(statement).all())
