"""Reusable submit-stage run metadata for :func:`commit_run_artifacts`."""

from __future__ import annotations

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import LlmTtaDfsConfig


def llm_tta_config_to_submit_dict(cfg: LlmTtaDfsConfig) -> dict[str, Any]:
    """Serialize ``LlmTtaDfsConfig`` for run metadata (JSON-friendly)."""
    return {
        "num_augmentations": int(cfg.num_augmentations),
        "execution_mode": str(cfg.execution_mode),
        "beam_width": int(cfg.beam_width),
        "max_candidates": int(cfg.max_candidates),
        "max_neg_log_score": float(cfg.max_neg_log_score),
        "seed": int(cfg.seed),
        "consistency_weight": float(cfg.consistency_weight),
        "model_weight": float(cfg.model_weight),
        "augmentation_likelihood_weight": float(cfg.augmentation_likelihood_weight),
        "enable_neural_backend": bool(cfg.enable_neural_backend),
        "model_path": cfg.model_path,
        "lora_path": cfg.lora_path,
        "max_runtime_sec": float(cfg.max_runtime_sec),
        "task_runtime_sec": float(cfg.task_runtime_sec),
        "decode_runtime_sec": float(cfg.decode_runtime_sec),
        "adapt_steps": int(cfg.adapt_steps),
        "adapt_batch_size": int(cfg.adapt_batch_size),
        "adapt_gradient_accumulation_steps": int(cfg.adapt_gradient_accumulation_steps),
        "adapt_disabled": bool(cfg.adapt_disabled),
        "per_task_adaptation": bool(cfg.per_task_adaptation),
        "runtime_attention_mode": str(cfg.runtime_attention_mode),
        "runtime_disable_compile": bool(cfg.runtime_disable_compile),
        "runtime_allocator_expandable_segments": bool(cfg.runtime_allocator_expandable_segments),
        "runtime_allocator_max_split_size_mb": int(cfg.runtime_allocator_max_split_size_mb),
        "prefer_cnn_attempt1": bool(cfg.prefer_cnn_attempt1),
        "candidate_ranker": str(cfg.candidate_ranker),
        "infer_artifact_dir": cfg.infer_artifact_dir,
        "infer_artifact_run_name": str(cfg.infer_artifact_run_name or ""),
    }


def build_submit_run_artifacts_patch(
    *,
    strategy: str,
    max_targets: int,
    models_list: list[str],
    primary_model: str,
    use_neural: bool,
    llm_cfg: LlmTtaDfsConfig,
    infer_artifact_final: dict[str, Any] | None,
    strategy_telemetry: dict[str, int],
    tuned_config_path: str | None,
    train_metadata_json: str | None,
    data_root: str,
    submission_json_src: str,
) -> dict[str, Any]:
    """Payload for :func:`commit_run_artifacts` (``patch`` argument)."""
    return {
        "config": {
            "submit": {
                "strategy": str(strategy),
                "max_targets": int(max_targets),
                "models": models_list,
                "primary_model": primary_model,
                "neural_infer": use_neural,
                "llm_tta_config": llm_tta_config_to_submit_dict(llm_cfg),
                "infer_artifact_final": (
                    {
                        "decoded_store_pkl": infer_artifact_final.get("decoded_store_pkl"),
                        "manifest_json": infer_artifact_final.get("manifest_json"),
                    }
                    if infer_artifact_final
                    else None
                ),
                "strategy_telemetry": dict(strategy_telemetry),
                "tuned_config_path": tuned_config_path,
                "train_metadata_json": train_metadata_json,
            }
        },
        "inputs": {"data_root": data_root},
        "artifacts": {"submission_json_src": submission_json_src},
    }