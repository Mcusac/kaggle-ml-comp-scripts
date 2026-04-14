"""Validate -> train -> submit pipeline shell for PipelineResult workflows."""

from dataclasses import dataclass
from typing import Any, Callable, Optional

from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult


@dataclass(frozen=True)
class ValidateTrainSubmitPipelineResultShell:
    """
    A thin shell for the common pattern:

      (optional) validate -> train -> submit

    Where validate/train/submit return PipelineResult and artifacts/metadata are merged.
    """

    stage: str
    data_root: str
    max_targets: int
    run_ctx: Optional[Any]
    validate_first: bool
    validate_fn: Callable[..., PipelineResult]
    train_fn: Callable[[], PipelineResult]
    submit_fn: Callable[[PipelineResult], PipelineResult]
    runner_fn: Callable[..., PipelineResult]

    train_stage: str = "train"
    submit_stage: str = "submit"

    def run(self) -> PipelineResult:
        return self.runner_fn(
            stage=str(self.stage),
            data_root=str(self.data_root),
            max_targets=int(self.max_targets),
            run_ctx=self.run_ctx,
            validate_first=bool(self.validate_first),
            validate_fn=self.validate_fn,
            first_stage=str(self.train_stage),
            first_fn=self.train_fn,
            second_stage=str(self.submit_stage),
            second_fn=self.submit_fn,
        )