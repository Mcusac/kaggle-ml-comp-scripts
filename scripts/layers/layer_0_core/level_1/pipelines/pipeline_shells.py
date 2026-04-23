"""Small, reusable orchestration shells for PipelineResult pipelines."""

from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar

from layers.layer_0_core.level_0 import PipelineResult

_T = TypeVar("_T")


class BasePipeline(Generic[_T]):
    """Minimal pipeline interface: a callable object with a single `run()`."""

    def run(self) -> _T:  # pragma: no cover (interface)
        raise NotImplementedError


@dataclass(frozen=True)
class ValidateFirstRunner(BasePipeline[_T]):
    """
    Validate-first shell for pipelines that signal failure via exceptions.

    This preserves the common pattern:
      validate(data_root, max_targets) -> run()
    without changing error-handling semantics (exceptions propagate).
    """

    validate_fn: Callable[..., None]
    run_fn: Callable[[], _T]
    data_root: str
    max_targets: int = 0

    def run(self) -> _T:
        self.validate_fn(data_root=self.data_root, max_targets=int(self.max_targets or 0))
        return self.run_fn()


@dataclass(frozen=True)
class ValidateFirstPipelineResultShell(BasePipeline[PipelineResult]):
    """Validate-first shell for PipelineResult-returning pipelines."""

    stage: str
    data_root: str
    max_targets: int
    run_ctx: Optional[Any]
    validate_first: bool
    validate_fn: Callable[..., PipelineResult]
    on_success: Callable[[], PipelineResult]
    runner_fn: Callable[..., PipelineResult]

    def run(self) -> PipelineResult:
        return self.runner_fn(
            stage=str(self.stage),
            data_root=str(self.data_root),
            max_targets=int(self.max_targets),
            run_ctx=self.run_ctx,
            validate_first=bool(self.validate_first),
            validate_fn=self.validate_fn,
            on_success=self.on_success,
        )


@dataclass(frozen=True)
class TwoStageValidateFirstPipelineResultShell(BasePipeline[PipelineResult]):
    """Validate-first shell for two-stage PipelineResult composites."""

    stage: str
    data_root: str
    max_targets: int
    run_ctx: Optional[Any]
    validate_first: bool
    validate_fn: Callable[..., PipelineResult]
    first_stage: str
    first_fn: Callable[[], PipelineResult]
    second_stage: str
    second_fn: Callable[[PipelineResult], PipelineResult]
    runner_fn: Callable[..., PipelineResult]

    def run(self) -> PipelineResult:
        return self.runner_fn(
            stage=str(self.stage),
            data_root=str(self.data_root),
            max_targets=int(self.max_targets),
            run_ctx=self.run_ctx,
            validate_first=bool(self.validate_first),
            validate_fn=self.validate_fn,
            first_stage=str(self.first_stage),
            first_fn=self.first_fn,
            second_stage=str(self.second_stage),
            second_fn=self.second_fn,
        )


