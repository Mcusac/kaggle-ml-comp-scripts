"""Validation and PipelineResult-oriented orchestration (including composites).

Subpackage replaces the monolithic ``orchestration.py``. Re-exports the six
public functions so ``level_6/__init__.py``'s ``from .orchestration import ...``
keeps resolving unchanged.
"""

from .composites import (
    run_train_and_submit_pipeline_result,
    run_tune_and_submit_pipeline_result,
)
from .single_stage import (
    run_submission_pipeline_result,
    run_train_pipeline_result,
    run_tune_pipeline_result,
)
from .validate import run_validate_data_pipeline

__all__ = [
    "run_validate_data_pipeline",
    "run_train_pipeline_result",
    "run_tune_pipeline_result",
    "run_submission_pipeline_result",
    "run_train_and_submit_pipeline_result",
    "run_tune_and_submit_pipeline_result",
]
