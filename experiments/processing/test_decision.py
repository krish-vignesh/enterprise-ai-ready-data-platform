import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.processing.execution.decision import ProcessingDecision, should_process_incremental
from app.processing.state.models import ProcessingState


def test_should_process_incremental_when_previous_state_is_missing() -> None:
    assert should_process_incremental(None, "hash-123") == ProcessingDecision.PROCESS


def test_should_skip_when_current_hash_matches_last_successful_hash() -> None:
    state = ProcessingState(
        dataset_name="sales",
        company_id="company-1",
        source_id="source-1",
        last_successful_file_hash="hash-123",
        updated_at=datetime(2026, 10, 3, 12, 0, 0),
    )

    assert should_process_incremental(state, "hash-123") == ProcessingDecision.SKIP


def test_should_process_when_hash_differs_from_last_successful_hash() -> None:
    state = ProcessingState(
        dataset_name="sales",
        company_id="company-1",
        source_id="source-1",
        last_successful_file_hash="hash-123",
        updated_at=datetime(2026, 10, 3, 12, 0, 0),
    )

    assert should_process_incremental(state, "hash-456") == ProcessingDecision.PROCESS


def test_should_validate_requires_current_hash_when_previous_state_exists() -> None:
    state = ProcessingState(
        dataset_name="sales",
        company_id="company-1",
        source_id="source-1",
        last_successful_file_hash="hash-123",
        updated_at=datetime(2026, 10, 3, 12, 0, 0),
    )

    with pytest.raises(ValueError):
        should_process_incremental(state, None)
