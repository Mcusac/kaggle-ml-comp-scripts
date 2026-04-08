"""Reusable orchestration shells for PipelineResult workflows."""

from .orchestration import (
    merge_pipeline_results_ok,
    run_pipeline_result_with_validation_first,
    run_two_stage_pipeline_result_with_validation_first,
)
from .pipeline_shells import (
    BasePipeline,
    ValidateFirstRunner,
    ValidateFirstPipelineResultShell,
    TwoStageValidateFirstPipelineResultShell,
)

__all__ = [
    "merge_pipeline_results_ok",
    "run_pipeline_result_with_validation_first",
    "run_two_stage_pipeline_result_with_validation_first",
    "BasePipeline",
    "ValidateFirstRunner",
    "ValidateFirstPipelineResultShell",
    "TwoStageValidateFirstPipelineResultShell",
]

