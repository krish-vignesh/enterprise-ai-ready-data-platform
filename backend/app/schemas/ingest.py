from pydantic import BaseModel

class IngestRequest(BaseModel):
    source: str
    dataset: str
    schema_version: str
    payload: dict

class IngestResponse(BaseModel):
    status: str
    message: str

