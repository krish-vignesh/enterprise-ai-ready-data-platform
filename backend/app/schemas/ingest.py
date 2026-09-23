from pydantic import BaseModel

class IngestRequest(BaseModel):
    source: str
    dataset: str
    schema_version: str
    payload: dict


class IngestFileRequest(BaseModel):
    source: str
    dataset: str
    schema_version: str


class IngestResponse(BaseModel):
    status: str
    message: str

