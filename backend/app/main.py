"""Application entry point."""

from fastapi import FastAPI

from app.api.document_batch import router as document_batch_router
from app.api.documents import router as documents_router
from app.api.ingest import router as ingest_router
from app.config.settings import settings
from app.middleware.request_id import RequestIDMiddleware


app = FastAPI()

app.add_middleware(RequestIDMiddleware)

# Single and batch document upload APIs.
app.include_router(documents_router)
app.include_router(document_batch_router)

# Legacy ingestion routes retained temporarily.
app.include_router(ingest_router)

print(settings.app_name)