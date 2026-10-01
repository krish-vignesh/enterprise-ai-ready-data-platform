from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class WorkspaceMetadata(BaseModel):
    workspace_id: str = Field(..., description="Unique identifier for the workspace.")
    notebook_name: str = Field(..., description="Notebook name for this workspace work product.")
    input_dataset: str = Field(..., description="Logical dataset name used as workspace input.")
    input_path: str = Field(..., description="Storage path for the input dataset.")
    output_path: str = Field(..., description="Storage path for workspace output.")
    created_at: datetime = Field(..., description="Timezone-aware creation timestamp.")
    updated_at: datetime = Field(..., description="Timezone-aware last update timestamp.")
    status: Literal["pending", "success", "failed"] = Field(
        default="pending",
        description="Lifecycle status for this workspace work product.",
    )

