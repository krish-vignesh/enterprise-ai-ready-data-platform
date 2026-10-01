import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

workspace_id = "workspace-validation"
notebook_name = "workspace_records_test"
notebook_object_path = f"workspaces/{workspace_id}/notebooks/{notebook_name}.ipynb"
metadata_object_path = f"workspaces/{workspace_id}/metadata/{notebook_name}.json"


try:
    from app.workspace.metadata import WorkspaceMetadata
    from app.workspace.notebook import read_notebook, save_notebook
    from app.workspace.storage import read_metadata, save_metadata
except Exception as exc:  # pragma: no cover - validation script must report runtime failures cleanly
    print(f"Notebook object path: {notebook_object_path}")
    print(f"Metadata object path: {metadata_object_path}")
    print("Notebook persistence: FAIL")
    print("Metadata persistence: FAIL")
    print(f"IMPORT ERROR: {exc}")
    print("OVERALL RESULT: FAIL")
    raise SystemExit(1)


def main() -> None:
    notebook_payload = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Workspace Records Validation\n", "This is an experiment.\n"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["print('workspace records ok')\n"],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    notebook_bytes = json.dumps(notebook_payload, indent=1).encode("utf-8")

    created_at = datetime.now(timezone.utc)
    metadata = WorkspaceMetadata(
        workspace_id=workspace_id,
        notebook_name=notebook_name,
        input_dataset="validation-dataset",
        input_path="datasets/validation/input",
        output_path=f"workspaces/{workspace_id}/notebooks/{notebook_name}.ipynb",
        created_at=created_at,
        updated_at=created_at,
        status="success",
    )

    print(f"Notebook object path: {notebook_object_path}")
    print(f"Metadata object path: {metadata_object_path}")

    notebook_ok = False
    metadata_ok = False

    try:
        saved_notebook_path = save_notebook(workspace_id, notebook_name, notebook_bytes)
        notebook_ok = saved_notebook_path == notebook_object_path
        print(f"Notebook save path: {saved_notebook_path}")
    except Exception as exc:  # pragma: no cover - validation script reports failures
        print(f"Notebook persistence: FAIL")
        print(f"Notebook save error: {exc}")

    try:
        saved_metadata_path = save_metadata(metadata)
        metadata_ok = saved_metadata_path == metadata_object_path
        print(f"Metadata save path: {saved_metadata_path}")
    except Exception as exc:  # pragma: no cover - validation script reports failures
        print(f"Metadata persistence: FAIL")
        print(f"Metadata save error: {exc}")

    if notebook_ok:
        try:
            notebook_read_back = read_notebook(workspace_id, notebook_name)
            notebook_ok = notebook_read_back == notebook_bytes
            print(f"Notebook persistence: {'PASS' if notebook_ok else 'FAIL'}")
        except Exception as exc:  # pragma: no cover - validation script reports failures
            notebook_ok = False
            print("Notebook persistence: FAIL")
            print(f"Notebook read error: {exc}")
    else:
        print("Notebook persistence: FAIL")

    if metadata_ok:
        try:
            metadata_read_back = read_metadata(workspace_id, notebook_name)
            metadata_ok = metadata_read_back.model_dump(mode="json") == metadata.model_dump(mode="json")
            print(f"Metadata persistence: {'PASS' if metadata_ok else 'FAIL'}")
        except Exception as exc:  # pragma: no cover - validation script reports failures
            metadata_ok = False
            print("Metadata persistence: FAIL")
            print(f"Metadata read error: {exc}")
    else:
        print("Metadata persistence: FAIL")

    print(f"OVERALL RESULT: {'PASS' if notebook_ok and metadata_ok else 'FAIL'}")


if __name__ == "__main__":
    main()
