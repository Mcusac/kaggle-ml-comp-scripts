"""Adapter implementing ``ContestPipelineProtocol`` for ARC path-based stages."""

from pathlib import Path
from typing import Any, Optional

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (
    run_submission_pipeline,
    run_train_pipeline,
    run_tune_pipeline,
)


class ArcContestPipeline:
    """Thin wrapper mapping protocol method names to ``run_*`` stage functions."""

    def train_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]:
        train_mode = str(kwargs.get("train_mode", "end_to_end"))
        models = kwargs.get("models") or ["baseline_approx"]
        if isinstance(models, str):
            models = [m.strip() for m in models.split(",") if m.strip()]
        max_targets = int(kwargs.get("max_targets", 0) or 0)
        return run_train_pipeline(
            data_root=data_root,
            train_mode=train_mode,
            models=list(models),
            run_ctx=kwargs.get("run_ctx"),
            max_targets=max_targets,
        )

    def submit_pipeline(self, data_root: str, strategy: str, **kwargs: Any) -> Path:
        raw_models = kwargs.get("models")
        models: Optional[list[str]] = None
        if isinstance(raw_models, str):
            models = [m.strip() for m in raw_models.split(",") if m.strip()]
        elif isinstance(raw_models, list):
            models = [str(m) for m in raw_models]
        return run_submission_pipeline(
            data_root=data_root,
            strategy=strategy,
            output_json=kwargs.get("output_json") or kwargs.get("output_csv"),
            max_targets=int(kwargs.get("max_targets", 0) or 0),
            run_ctx=kwargs.get("run_ctx"),
            tuned_config_path=kwargs.get("tuned_config_path") or kwargs.get("tuned_config"),
            train_metadata_json=kwargs.get("train_metadata_json"),
            models=models,
            neural_checkpoint_path=kwargs.get("neural_checkpoint_path"),
            neural_train_config_path=kwargs.get("neural_train_config_path"),
            train_mode=str(kwargs.get("train_mode", "end_to_end")),
            llm_execution_mode=str(kwargs.get("llm_execution_mode", "surrogate") or "surrogate"),
            llm_num_augmentations=int(kwargs.get("llm_num_augmentations", 8) or 8),
            llm_beam_width=int(kwargs.get("llm_beam_width", 12) or 12),
            llm_max_candidates=int(kwargs.get("llm_max_candidates", 6) or 6),
            llm_max_neg_log_score=float(kwargs.get("llm_max_neg_log_score", 120.0) or 120.0),
            llm_seed=int(kwargs.get("llm_seed", 0) or 0),
            llm_consistency_weight=float(kwargs.get("llm_consistency_weight", 1.0) or 1.0),
            llm_model_weight=float(kwargs.get("llm_model_weight", 1.0) or 1.0),
            llm_augmentation_likelihood_weight=float(
                kwargs.get("llm_augmentation_likelihood_weight", 1.0) or 1.0
            ),
            llm_enable_neural_backend=bool(kwargs.get("llm_enable_neural_backend", False)),
            llm_model_path=kwargs.get("llm_model_path"),
            llm_lora_path=kwargs.get("llm_lora_path"),
            llm_max_runtime_sec=float(kwargs.get("llm_max_runtime_sec", 0.0) or 0.0),
            llm_task_runtime_sec=float(kwargs.get("llm_task_runtime_sec", 0.0) or 0.0),
            llm_decode_runtime_sec=float(kwargs.get("llm_decode_runtime_sec", 0.0) or 0.0),
            llm_adapt_steps=int(kwargs.get("llm_adapt_steps", 0) or 0),
            llm_adapt_batch_size=int(kwargs.get("llm_adapt_batch_size", 1) or 1),
            llm_adapt_gradient_accumulation_steps=int(
                kwargs.get("llm_adapt_gradient_accumulation_steps", 1) or 1
            ),
            llm_adapt_disabled=bool(kwargs.get("llm_adapt_disabled", False)),
            llm_per_task_adaptation=bool(kwargs.get("llm_per_task_adaptation", False)),
            llm_runtime_attention_mode=str(kwargs.get("llm_runtime_attention_mode", "auto") or "auto"),
            llm_runtime_disable_compile=bool(kwargs.get("llm_runtime_disable_compile", False)),
            llm_runtime_allocator_expandable_segments=bool(
                kwargs.get("llm_runtime_allocator_expandable_segments", True)
            ),
            llm_runtime_allocator_max_split_size_mb=int(
                kwargs.get("llm_runtime_allocator_max_split_size_mb", 0) or 0
            ),
            llm_prefer_cnn_attempt1=bool(kwargs.get("llm_prefer_cnn_attempt1", False)),
            llm_candidate_ranker=str(kwargs.get("llm_candidate_ranker", "default") or "default"),
            llm_infer_artifact_dir=kwargs.get("llm_infer_artifact_dir"),
            llm_infer_artifact_run_name=str(kwargs.get("llm_infer_artifact_run_name", "") or ""),
        )

    def tune_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]:
        model_name = str(kwargs.get("model_name", kwargs.get("model", "baseline_approx")))
        search_type = str(kwargs.get("search_type", "quick"))
        max_targets = int(kwargs.get("max_targets", 0) or 0)
        return run_tune_pipeline(
            data_root=data_root,
            model_name=model_name,
            search_type=search_type,
            max_targets=max_targets,
            run_ctx=kwargs.get("run_ctx"),
        )
