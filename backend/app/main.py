"""Application entry point."""

from fastapi import FastAPI


from app.api.companies import router as companies_router
from app.api.document_batch import router as document_batch_router
from app.api.documents import router as documents_router
from app.api.ingest import router as ingest_router
from app.api.source_systems import router as source_systems_router

from app.config.settings import settings
from app.middleware.request_id import RequestIDMiddleware
from app.lifespan import lifespan
from app.api.datasets import router as datasets_router


app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)

# Company registration APIs.
app.include_router(companies_router)

# Single and batch document upload APIs.
app.include_router(documents_router)

# Source system APIs.
app.include_router(source_systems_router)

# Document batch APIs.
app.include_router(document_batch_router)

# Legacy ingestion routes retained temporarily.
app.include_router(ingest_router)

# Dataset catalog APIs.
app.include_router(datasets_router)

print(settings.app_name)
