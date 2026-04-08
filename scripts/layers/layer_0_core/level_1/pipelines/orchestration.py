"""Reusable validate-then-run patterns for PipelineResult workflows."""

from typing import Any, Callable, Optional

from level_0 import PipelineResult


def run_pipeline_result_with_validation_first(
    *,
    stage: str,
    data_root: str,
    max_targets: int,
    run_ctx: Optional[Any],
    validate_first: bool,
    validate_fn: Callable[..., PipelineResult],
    on_success: Callable[[], PipelineResult],
) -> PipelineResult:
    """If validate_first, run validate_fn; on success call on_success and return its PipelineResult."""
    if validate_first:
        validation = validate_fn(data_root=data_root, max_targets=max_targets, run_ctx=run_ctx)
        if not validation.success:
            return PipelineResult.fail(
                stage=str(stage),
                error=validation.error or "Validation failed",
                metadata={"blocked_by": "validate_data", **dict(validation.metadata)},
            )
    try:
        result = on_success()
        if isinstance(result, PipelineResult):
            return result
        return PipelineResult.fail(
            stage=str(stage),
            error="Pipeline returned unexpected result type",
            metadata={"blocked_by": None},
        )
    except Exception as e:
        return PipelineResult.fail(stage=str(stage), error=str(e), metadata={"error_repr": repr(e)})


def merge_pipeline_results_ok(*, stage: str, a: PipelineResult, b: PipelineResult) -> PipelineResult:
    """Combine two successful results (artifacts + metadata); both should be success."""
    meta_a = dict(a.metadata) if a.metadata else {}
    meta_b = dict(b.metadata) if b.metadata else {}
    return PipelineResult.ok(
        stage=str(stage),
        artifacts={**dict(a.artifacts), **dict(b.artifacts)},
        metadata={**meta_a, **meta_b},
    )


def run_two_stage_pipeline_result_with_validation_first(
    *,
    stage: str,
    data_root: str,
    max_targets: int,
    run_ctx: Optional[Any],
    validate_first: bool,
    validate_fn: Callable[..., PipelineResult],
    first_stage: str,
    first_fn: Callable[[], PipelineResult],
    second_stage: str,
    second_fn: Callable[[PipelineResult], PipelineResult],
) -> PipelineResult:
    """
    Run a two-stage PipelineResult workflow with an optional shared validation step.
    """

    def _on_success() -> PipelineResult:
        first = first_fn()
        if not isinstance(first, PipelineResult):
            return PipelineResult.fail(stage=str(first_stage), error="First stage returned unexpected result type")
        if not first.success:
            return first

        second = second_fn(first)
        if not isinstance(second, PipelineResult):
            return PipelineResult.fail(stage=str(second_stage), error="Second stage returned unexpected result type")
        if not second.success:
            return second

        return merge_pipeline_results_ok(stage=str(stage), a=first, b=second)

    return run_pipeline_result_with_validation_first(
        stage=str(stage),
        data_root=str(data_root),
        max_targets=int(max_targets),
        run_ctx=run_ctx,
        validate_first=bool(validate_first),
        validate_fn=validate_fn,
        on_success=_on_success,
    )


