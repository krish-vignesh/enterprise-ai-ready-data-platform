"""Repository for Document persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    """Persistence operations for Document records."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, document_id: int) -> Document | None:
        """Fetch a document by its primary key."""
        return self.session.get(Document, document_id)

    def list_by_dataset(self, dataset_id: int) -> list[Document]:
        """Return all documents attached to a dataset."""
        statement = select(Document).where(Document.dataset_id == dataset_id)
        return list(self.session.scalars(statement).all())
