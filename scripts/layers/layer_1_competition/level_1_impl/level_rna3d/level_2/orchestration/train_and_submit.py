"""RNA3D composite pipeline: validate -> train -> submit (PipelineResult wrapper)."""

from __future__ import annotations

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult, contest_models_dir
from layers.layer_1_competition.level_0_infra.level_1 import run_two_stage_pipeline_result_with_validation_first
from layers.layer_1_competition.level_0_infra.level_0.artifacts import (
    capture_model_paths,
    capture_submission_paths,
    metadata_merge,
)
from layers.layer_1_competition.level_0_infra.level_1.pipelines import ValidateTrainSubmitPipelineResultShell

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import RNA3DPaths, validate_rna3d_inputs
from layers.layer_1_competition.level_1_impl.level_rna3d.level_2.orchestration.submission import submit_pipeline
from layers.layer_1_competition.level_1_impl.level_rna3d.level_3.training.pipeline import train_pipeline


def _validate_rna3d_pipeline_result(*, data_root: str, max_targets: int = 0, run_ctx: object | None = None) -> PipelineResult:
    try:
        validate_rna3d_inputs(data_root=data_root, max_targets=int(max_targets or 0))
        return PipelineResult.ok(
            stage="validate_data",
            metadata=metadata_merge({"data_root": str(data_root), "max_targets": int(max_targets or 0)}),
        )
    except Exception as e:
        return PipelineResult.fail(
            stage="validate_data",
            error=str(e),
            metadata=metadata_merge({"error_repr": repr(e)}),
        )


def run_train_and_submit_pipeline_result(
    *,
    data_root: str,
    train_mode: str,
    models: List[str],
    strategy: str,
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    validate_first: bool = True,
) -> PipelineResult:
    paths = RNA3DPaths()
    output_base = contest_models_dir(paths, "rna3d")

    def _train() -> PipelineResult:
        try:
            train_pipeline(
                data_root=data_root,
                train_mode=train_mode,
                models=models,
                validate_first=False,
            )
            return PipelineResult.ok(
                stage="train",
                artifacts=capture_model_paths(models_dir=str(output_base)),
                metadata=metadata_merge({"train_mode": str(train_mode), "models": list(models)}),
            )
        except Exception as e:
            return PipelineResult.fail(stage="train", error=str(e), metadata={"error_repr": repr(e)})

    def _submit(_train_result: PipelineResult) -> PipelineResult:
        try:
            out_path = submit_pipeline(
                data_root=data_root,
                strategy=strategy,
                models=models,
                output_csv=output_csv,
                max_targets=max_targets,
                ensemble_weights=ensemble_weights,
                use_validation_for_stacking=use_validation_for_stacking,
                validate_first=False,
            )
            return PipelineResult.ok(
                stage="submit",
                artifacts=capture_submission_paths(submission_csv=str(out_path)),
                metadata=metadata_merge({"strategy": str(strategy), "models": list(models)}),
            )
        except Exception as e:
            return PipelineResult.fail(stage="submit", error=str(e), metadata={"error_repr": repr(e)})

    return ValidateTrainSubmitPipelineResultShell(
        stage="train_and_submit",
        data_root=data_root,
        max_targets=int(max_targets or 0),
        run_ctx=None,
        validate_first=bool(validate_first),
        validate_fn=_validate_rna3d_pipeline_result,
        train_fn=_train,
        submit_fn=_submit,
        runner_fn=run_two_stage_pipeline_result_with_validation_first,
    ).run()


__all__ = ["run_train_and_submit_pipeline_result"]

