"""ARC level_1: contest-local orchestration support utilities.

Level 1 holds shared helpers for contest stages (level_2), orchestration (level_3),
and handlers (e.g., run tracking, PipelineResult).
"""

from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult
from .model import TinyGridCNN
from .run_tracking import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    init_run_context,
    update_run_metadata,
)

__all__ = [
    "PipelineResult",
    "RunContext",
    "TinyGridCNN",
    "copy_artifact_into_run",
    "finalize_run_failure",
    "finalize_run_success",
    "init_run_context",
    "update_run_metadata",
]

