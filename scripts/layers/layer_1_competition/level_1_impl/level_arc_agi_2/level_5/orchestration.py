"""Validation and PipelineResult-oriented orchestration (including composites)."""

from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import (
    run_pipeline_result_with_validation_first,
    ValidateTrainSubmitPipelineResultShell,
    ArtifactKeys,
    capture_config_paths,
    capture_submission_paths,
    metadata_merge,
    validate_arc_inputs,
)
from layers.layer_1_competition.level_0_infra.level_1 import (
    TwoStageValidateFirstPipelineResultShell,
    run_two_stage_pipeline_result_with_validation_first,
    PipelineResult,
    RunContext,
    update_run_metadata,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (
    run_submission_pipeline,
    run_train_pipeline,
    run_tune_pipeline,
)


def run_validate_data_pipeline(
    *,
    data_root: str,
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
) -> PipelineResult:
    """Validate ARC inputs (standalone pipeline stage)."""
    try:
        validate_arc_inputs(data_root=str(data_root), max_targets=int(max_targets or 0))
        if run_ctx is not None:
            update_run_metadata(
                run_ctx,
                {
                    "config": {"validate_data": {"max_targets": int(max_targets or 0)}},
                    "inputs": {"data_root": str(data_root)},
                    "validation": {"status": "success"},
                },
            )
        return PipelineResult.ok(
            stage="validate_data",
            metadata=metadata_merge({"data_root": str(data_root), "max_targets": int(max_targets or 0)}),
        )
    except Exception as e:
        if run_ctx is not None:
            try:
                update_run_metadata(
                    run_ctx,
                    {
                        "config": {"validate_data": {"max_targets": int(max_targets or 0)}},
                        "inputs": {"data_root": str(data_root)},
                        "validation": {"status": "failed", "error": repr(e)},
                    },
                )
            except Exception:
                pass
        return PipelineResult.fail(
            stage="validate_data",
            error=str(e),
            metadata=metadata_merge({"data_root": str(data_root), "max_targets": int(max_targets or 0), "error_repr": repr(e)}),
        )


def run_train_pipeline_result(
    *,
    data_root: str,
    train_mode: str,
    models: list[str],
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    validate_first: bool = True,
) -> PipelineResult:
    return run_pipeline_result_with_validation_first(
        stage="train",
        data_root=data_root,
        max_targets=max_targets,
        run_ctx=run_ctx,
        validate_first=validate_first,
        validate_fn=run_validate_data_pipeline,
        on_success=lambda: PipelineResult.ok(
            stage="train",
            artifacts=capture_config_paths(
                train_metadata_json=str(
                    run_train_pipeline(
                        data_root=data_root,
                        train_mode=train_mode,
                        models=models,
                        run_ctx=run_ctx,
                        max_targets=max_targets,
                    )
                )
            ),
        ),
    )


def run_tune_pipeline_result(
    *,
    data_root: str,
    model_name: str,
    search_type: str = "quick",
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    validate_first: bool = True,
) -> PipelineResult:
    return run_pipeline_result_with_validation_first(
        stage="tune",
        data_root=data_root,
        max_targets=max_targets,
        run_ctx=run_ctx,
        validate_first=validate_first,
        validate_fn=run_validate_data_pipeline,
        on_success=lambda: PipelineResult.ok(
            stage="tune",
            artifacts=capture_config_paths(
                best_config_json=str(
                    run_tune_pipeline(
                        data_root=data_root,
                        model_name=model_name,
                        search_type=search_type,
                        max_targets=max_targets,
                        run_ctx=run_ctx,
                    )
                )
            ),
        ),
    )


def run_submission_pipeline_result(
    *,
    data_root: str,
    strategy: str,
    output_json: Optional[str] = None,
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    validate_first: bool = True,
    tuned_config_path: Optional[str] = None,
    train_metadata_json: Optional[str] = None,
    models: Optional[list[str]] = None,
    neural_checkpoint_path: Optional[str] = None,
    neural_train_config_path: Optional[str] = None,
    train_mode: str = "end_to_end",
) -> PipelineResult:
    def _on_success() -> PipelineResult:
        return PipelineResult.ok(
            stage="submit",
            artifacts=capture_submission_paths(
                submission_json=str(
                    run_submission_pipeline(
                        data_root=data_root,
                        strategy=strategy,
                        output_json=output_json,
                        max_targets=max_targets,
                        run_ctx=run_ctx,
                        tuned_config_path=str(tuned_config_path) if tuned_config_path else None,
                        train_metadata_json=str(train_metadata_json) if train_metadata_json else None,
                        models=models,
                        neural_checkpoint_path=neural_checkpoint_path,
                        neural_train_config_path=neural_train_config_path,
                        train_mode=train_mode,
                    )
                )
            ),
        )

    return run_pipeline_result_with_validation_first(
        stage="submit",
        data_root=data_root,
        max_targets=max_targets,
        run_ctx=run_ctx,
        validate_first=validate_first,
        validate_fn=run_validate_data_pipeline,
        on_success=_on_success,
    )


def run_train_and_submit_pipeline_result(
    *,
    data_root: str,
    train_mode: str,
    models: list[str],
    strategy: str,
    output_json: Optional[str] = None,
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    validate_first: bool = True,
) -> PipelineResult:
    return ValidateTrainSubmitPipelineResultShell(
        stage="train_and_submit",
        data_root=data_root,
        max_targets=max_targets,
        run_ctx=run_ctx,
        validate_first=validate_first,
        validate_fn=run_validate_data_pipeline,
        train_stage="train",
        train_fn=lambda: run_train_pipeline_result(
            data_root=data_root,
            train_mode=train_mode,
            models=models,
            max_targets=max_targets,
            run_ctx=run_ctx,
            validate_first=False,
        ),
        submit_stage="submit",
        submit_fn=lambda train_result: run_submission_pipeline_result(
            data_root=data_root,
            strategy=strategy,
            output_json=output_json,
            max_targets=max_targets,
            run_ctx=run_ctx,
            validate_first=False,
            tuned_config_path=None,
            train_metadata_json=(str(train_result.artifacts.get(ArtifactKeys.TRAIN_METADATA_JSON, "")).strip() or None),
            models=models,
            train_mode=train_mode,
        ),
        runner_fn=run_two_stage_pipeline_result_with_validation_first,
    ).run()


def run_tune_and_submit_pipeline_result(
    *,
    data_root: str,
    model_name: str,
    search_type: str = "quick",
    strategy: str,
    output_json: Optional[str] = None,
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    validate_first: bool = True,
) -> PipelineResult:
    return TwoStageValidateFirstPipelineResultShell(
        stage="tune_and_submit",
        data_root=data_root,
        max_targets=max_targets,
        run_ctx=run_ctx,
        validate_first=validate_first,
        validate_fn=run_validate_data_pipeline,
        first_stage="tune",
        first_fn=lambda: run_tune_pipeline_result(
            data_root=data_root,
            model_name=model_name,
            search_type=search_type,
            max_targets=max_targets,
            run_ctx=run_ctx,
            validate_first=False,
        ),
        second_stage="submit",
        second_fn=lambda tune_result: run_submission_pipeline_result(
            data_root=data_root,
            strategy=strategy,
            output_json=output_json,
            max_targets=max_targets,
            run_ctx=run_ctx,
            validate_first=False,
            tuned_config_path=(str(tune_result.artifacts.get(ArtifactKeys.BEST_CONFIG_JSON, "")).strip() or None),
            train_metadata_json=None,
            models=[str(model_name)],
            train_mode="end_to_end",
        ),
        runner_fn=run_two_stage_pipeline_result_with_validation_first,
    ).run()
