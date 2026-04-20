"""Single-stage ``PipelineResult`` wrappers: train / tune / submit."""

from typing import Optional

from layers.layer_0_core.level_0 import PipelineResult
from layers.layer_0_core.level_1 import run_pipeline_result_with_validation_first

from layers.layer_1_competition.level_0_infra.level_0 import (
    capture_config_paths,
    capture_submission_paths,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    RunContext,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    run_validate_data_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (
    run_train_pipeline,
    run_tune_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (
    run_submission_pipeline,

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
    llm_num_augmentations: int = 8,
    llm_execution_mode: str = "surrogate",
    llm_beam_width: int = 12,
    llm_max_candidates: int = 6,
    llm_max_neg_log_score: float = 120.0,
    llm_seed: int = 0,
    llm_consistency_weight: float = 1.0,
    llm_model_weight: float = 1.0,
    llm_augmentation_likelihood_weight: float = 1.0,
    llm_enable_neural_backend: bool = False,
    llm_model_path: Optional[str] = None,
    llm_lora_path: Optional[str] = None,
    llm_max_runtime_sec: float = 0.0,
    llm_task_runtime_sec: float = 0.0,
    llm_decode_runtime_sec: float = 0.0,
    llm_adapt_steps: int = 0,
    llm_adapt_batch_size: int = 1,
    llm_adapt_gradient_accumulation_steps: int = 1,
    llm_adapt_disabled: bool = False,
    llm_per_task_adaptation: bool = False,
    llm_runtime_attention_mode: str = "auto",
    llm_runtime_disable_compile: bool = False,
    llm_runtime_allocator_expandable_segments: bool = True,
    llm_runtime_allocator_max_split_size_mb: int = 0,
    llm_prefer_cnn_attempt1: bool = False,
    llm_candidate_ranker: str = "default",
    llm_infer_artifact_dir: Optional[str] = None,
    llm_infer_artifact_run_name: str = "",
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
                        llm_execution_mode=llm_execution_mode,
                        llm_num_augmentations=llm_num_augmentations,
                        llm_beam_width=llm_beam_width,
                        llm_max_candidates=llm_max_candidates,
                        llm_max_neg_log_score=llm_max_neg_log_score,
                        llm_seed=llm_seed,
                        llm_consistency_weight=llm_consistency_weight,
                        llm_model_weight=llm_model_weight,
                        llm_augmentation_likelihood_weight=llm_augmentation_likelihood_weight,
                        llm_enable_neural_backend=llm_enable_neural_backend,
                        llm_model_path=llm_model_path,
                        llm_lora_path=llm_lora_path,
                        llm_max_runtime_sec=llm_max_runtime_sec,
                        llm_task_runtime_sec=llm_task_runtime_sec,
                        llm_decode_runtime_sec=llm_decode_runtime_sec,
                        llm_adapt_steps=llm_adapt_steps,
                        llm_adapt_batch_size=llm_adapt_batch_size,
                        llm_adapt_gradient_accumulation_steps=llm_adapt_gradient_accumulation_steps,
                        llm_adapt_disabled=llm_adapt_disabled,
                        llm_per_task_adaptation=llm_per_task_adaptation,
                        llm_runtime_attention_mode=llm_runtime_attention_mode,
                        llm_runtime_disable_compile=llm_runtime_disable_compile,
                        llm_runtime_allocator_expandable_segments=llm_runtime_allocator_expandable_segments,
                        llm_runtime_allocator_max_split_size_mb=llm_runtime_allocator_max_split_size_mb,
                        llm_prefer_cnn_attempt1=llm_prefer_cnn_attempt1,
                        llm_candidate_ranker=llm_candidate_ranker,
                        llm_infer_artifact_dir=llm_infer_artifact_dir,
                        llm_infer_artifact_run_name=llm_infer_artifact_run_name,
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
