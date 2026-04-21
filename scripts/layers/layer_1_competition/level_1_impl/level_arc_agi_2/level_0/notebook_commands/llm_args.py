"""Thin wrapper so ``cmd_*`` builders can call :func:`append_llm_args` as ``append_llm``."""

from typing import Any, List

from layers.layer_1_competition.level_0_infra.level_0.argv_command_builders import (
    append_llm_args,
)

_DEFAULT_LLM_TTA_KWARGS: dict[str, Any] = {
    "llm_execution_mode": "surrogate",
    "llm_num_augmentations": 8,
    "llm_beam_width": 12,
    "llm_max_candidates": 6,
    "llm_max_neg_log_score": 120.0,
    "llm_seed": 0,
    "llm_consistency_weight": 1.0,
    "llm_model_weight": 1.0,
    "llm_enable_neural_backend": False,
    "llm_model_path": None,
    "llm_lora_path": None,
    "llm_max_runtime_sec": 0.0,
    "llm_task_runtime_sec": 0.0,
    "llm_decode_runtime_sec": 0.0,
    "llm_adapt_steps": 0,
    "llm_adapt_batch_size": 1,
    "llm_adapt_gradient_accumulation_steps": 1,
    "llm_adapt_disabled": False,
    "llm_per_task_adaptation": False,
    "llm_augmentation_likelihood_weight": 1.0,
    "llm_runtime_attention_mode": "auto",
    "llm_runtime_disable_compile": False,
    "llm_runtime_allocator_expandable_segments": True,
    "llm_runtime_allocator_max_split_size_mb": 0,
    "llm_prefer_cnn_attempt1": False,
    "llm_infer_artifact_dir": None,
    "llm_infer_artifact_run_name": "",
}


def append_llm(cmd: List[str], strategy: str, **kwargs: Any) -> None:
    """Merge ``kwargs`` over CLI defaults, then append flags when strategy is ``llm_tta_dfs``."""
    m: dict[str, Any] = {**_DEFAULT_LLM_TTA_KWARGS, **kwargs}
    append_llm_args(
        cmd,
        strategy=strategy,
        llm_execution_mode=m["llm_execution_mode"],
        llm_num_augmentations=int(m["llm_num_augmentations"] or 8),
        llm_beam_width=int(m["llm_beam_width"] or 12),
        llm_max_candidates=int(m["llm_max_candidates"] or 6),
        llm_max_neg_log_score=float(m["llm_max_neg_log_score"] or 120.0),
        llm_seed=int(m["llm_seed"] or 0),
        llm_consistency_weight=float(m["llm_consistency_weight"] or 1.0),
        llm_model_weight=float(m["llm_model_weight"] or 1.0),
        llm_enable_neural_backend=bool(m["llm_enable_neural_backend"]),
        llm_model_path=m["llm_model_path"],
        llm_lora_path=m["llm_lora_path"],
        llm_max_runtime_sec=float(m["llm_max_runtime_sec"] or 0.0),
        llm_task_runtime_sec=float(m["llm_task_runtime_sec"] or 0.0),
        llm_decode_runtime_sec=float(m["llm_decode_runtime_sec"] or 0.0),
        llm_adapt_steps=int(m["llm_adapt_steps"] or 0),
        llm_adapt_batch_size=int(m["llm_adapt_batch_size"] or 1),
        llm_adapt_gradient_accumulation_steps=int(
            m["llm_adapt_gradient_accumulation_steps"] or 1
        ),
        llm_adapt_disabled=bool(m["llm_adapt_disabled"]),
        llm_per_task_adaptation=bool(m["llm_per_task_adaptation"]),
        llm_augmentation_likelihood_weight=float(
            m["llm_augmentation_likelihood_weight"] or 1.0
        ),
        llm_runtime_attention_mode=str(m["llm_runtime_attention_mode"] or "auto"),
        llm_runtime_disable_compile=bool(m["llm_runtime_disable_compile"]),
        llm_runtime_allocator_expandable_segments=bool(
            m["llm_runtime_allocator_expandable_segments"]
        ),
        llm_runtime_allocator_max_split_size_mb=int(
            m["llm_runtime_allocator_max_split_size_mb"] or 0
        ),
        llm_prefer_cnn_attempt1=bool(m["llm_prefer_cnn_attempt1"]),
        llm_infer_artifact_dir=m["llm_infer_artifact_dir"],
        llm_infer_artifact_run_name=str(m["llm_infer_artifact_run_name"] or ""),
    )
