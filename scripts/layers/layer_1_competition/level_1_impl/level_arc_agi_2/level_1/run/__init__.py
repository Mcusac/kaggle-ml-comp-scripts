"""ARC-AGI-2 run-tracking subpackage.

Re-exports the public surface of the original `run_tracking.py` module so
external callers continue to work after the SRP split.
"""

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.run.finalize import (
    commit_run_artifacts,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.run.run_context import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    init_run_context,
    update_run_metadata,
)
from .run_dir import default_runs_root, resolve_run_dir
from .run_id import generate_run_id

__all__ = [
    "RunContext",
    "commit_run_artifacts",
    "copy_artifact_into_run",
    "default_runs_root",
    "finalize_run_failure",
    "finalize_run_success",
    "generate_run_id",
    "init_run_context",
    "resolve_run_dir",
    "update_run_metadata",
]
