from io import BytesIO

from app.config.settings import settings
from app.storage.minio_client import client

BUCKET_NAME = settings.workspace_records_bucket


def _notebook_object_path(workspace_id: str, notebook_name: str) -> str:
    return f"workspaces/{workspace_id}/notebooks/{notebook_name}.ipynb"


def save_notebook(workspace_id: str, notebook_name: str, notebook_content: bytes | str) -> str:
    object_name = _notebook_object_path(workspace_id, notebook_name)
    payload = (
        notebook_content.encode("utf-8")
        if isinstance(notebook_content, str)
        else notebook_content
    )
    payload_stream = BytesIO(payload)

    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        data=payload_stream,
        length=len(payload),
        content_type="application/x-ipynb+json",
    )

    return object_name


def read_notebook(workspace_id: str, notebook_name: str) -> bytes:
    object_name = _notebook_object_path(workspace_id, notebook_name)
    response = client.get_object(BUCKET_NAME, object_name)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()
