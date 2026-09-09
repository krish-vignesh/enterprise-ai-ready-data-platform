from fastapi import APIRouter
from app.schemas.ingest import IngestRequest, IngestResponse
from app.services.ingest import ingest_data

router = APIRouter() #Router - buz we gonna create all the route he and connect with main

@router.post("/ingest", response_model=IngestResponse) #/ingest → url, response_model =  saying system we have respose class aswell
def ingest(request: IngestRequest): # the backend & first layer has to cm in function parameter
    return ingest_data(request)

