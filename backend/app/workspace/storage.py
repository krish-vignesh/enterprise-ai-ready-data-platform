import json
from io import BytesIO

from app.config.settings import settings
from app.storage.minio_client import client
from app.workspace.metadata import WorkspaceMetadata


BUCKET_NAME = settings.workspace_records_bucket


def _metadata_object_path(workspace_id: str, notebook_name: str) -> str:
    return f"workspaces/{workspace_id}/metadata/{notebook_name}.json"


def save_metadata(metadata: WorkspaceMetadata) -> str:
    object_name = _metadata_object_path(metadata.workspace_id, metadata.notebook_name)
    payload = json.dumps(metadata.model_dump(mode="json")).encode("utf-8")
    payload_stream = BytesIO(payload)

    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        data=payload_stream,
        length=len(payload),
        content_type="application/json",
    )

    return object_name


def read_metadata(workspace_id: str, notebook_name: str) -> WorkspaceMetadata:
    object_name = _metadata_object_path(workspace_id, notebook_name)
    response = client.get_object(BUCKET_NAME, object_name)
    try:
        metadata_payload = json.loads(response.read().decode("utf-8"))
    finally:
        response.close()
        response.release_conn()

    return WorkspaceMetadata(**metadata_payload)
