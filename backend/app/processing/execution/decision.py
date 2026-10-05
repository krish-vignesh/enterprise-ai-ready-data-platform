from enum import Enum

from app.processing.state.models import ProcessingState


class ProcessingDecision(str, Enum):
    """Explicit outcome for an incremental-processing decision."""

    PROCESS = "PROCESS"
    SKIP = "SKIP"


def should_process_incremental(
    previous_state: ProcessingState | None,
    current_file_hash: str | None,
) -> ProcessingDecision:
    """Decide whether incremental processing should continue for the current artifact.

    A None previous_state means there is no prior successful ProcessingState for
    this dataset/company/source scope, so this is the first-ever processing run
    and the request is eligible for processing.

    When a previous state exists, the current artifact hash is compared to the last
    successful hash stored in that state. If they match, the artifact is unchanged
    and incremental processing is skipped.

    Later rules are intentionally not decided here; this function covers the three
    currently defined incremental cases only.
    """
    if previous_state is None:
        return ProcessingDecision.PROCESS

    if current_file_hash is None:
        raise ValueError("current_file_hash is required when a previous state exists.")

    if current_file_hash == previous_state.last_successful_file_hash:
        return ProcessingDecision.SKIP

    return ProcessingDecision.PROCESS


__all__ = ["ProcessingDecision", "should_process_incremental"]
