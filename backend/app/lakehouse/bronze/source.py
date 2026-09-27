from pydantic import BaseModel, Field


class SourceArtifact(BaseModel):
    """Contract for the original source artifact preserved for Bronze ingestion.

    This model identifies the company, source system/channel, and object-storage
    location of the original file before it is represented in the managed Bronze
    layer.
    """

    company_id: str = Field(..., description="Existing company identifier associated with the source artifact.")
    company_name: str = Field(..., description="Human-readable company name.")
    source_id: str = Field(..., description="Identifier of the source system or source channel that produced the data.")
    source_object_path: str = Field(..., description="Object-storage path where the original source artifact is preserved.")
