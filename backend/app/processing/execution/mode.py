from enum import Enum
#enum means enumeration, which is a set of symbolic names (members) bound to unique, constant values. In this case, the ExecutionMode class is an enumeration that defines two possible execution modes for a processing run: FULL and INCREMENTAL.


class ExecutionMode(str, Enum):
    """Execution mode selected for a processing run.

    FULL means a full processing execution was requested.
    INCREMENTAL means incremental processing was requested.
    This module represents the mode only; it does not execute processing.
    """

    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"


__all__ = ["ExecutionMode"]
