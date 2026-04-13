"""
Solver v2 — entry point.

Identical to v1 except ``accelerate.utils.GradScalerKwargs`` is imported at
module level (not inside the redirect block), which avoids a rare import-ordering
issue in some Accelerate versions.  All other config values are the same as v1.
"""

# Eagerly import GradScalerKwargs at module level (the v1 vs v2 distinction).
from accelerate.utils import GradScalerKwargs  # noqa: F401

from .worker_v1 import V1_CONFIG, worker_core


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def worker(rank: int, queue, end_time: float) -> None:
    """Same config as v1 — GradScalerKwargs is simply guaranteed to be imported first."""
    worker_core(rank, queue, end_time, V1_CONFIG)