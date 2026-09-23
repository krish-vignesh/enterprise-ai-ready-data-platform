from fastapi import APIRouter
from app.schemas.ingest import IngestRequest, IngestResponse, IngestFileRequest
from app.services.ingest import ingest_data, ingest_file_data
from typing import Annotated
from fastapi import Form, UploadFile, File
router = APIRouter() #Router - buz we gonna create all the route he and connect with main

@router.post("/ingest", response_model=IngestResponse) #/ingest → url, response_model =  saying system we have respose class aswell
def ingest(request: IngestRequest): # the backend & first layer has to cm in function parameter
    return ingest_data(request)



@router.post("/ingest/file", response_model=IngestResponse)
def ingest_file(
    source: str = Form(...),
    dataset: str = Form(...),
    schema_version: str = Form(...),
    file: UploadFile = File(...),
):
    metadata = IngestFileRequest(
        source=source,
        dataset=dataset,
        schema_version=schema_version,
    )

    return ingest_file_data(metadata, file)