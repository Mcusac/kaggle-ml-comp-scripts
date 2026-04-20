"""argparse -> LLM-TTA kwargs adapter.

Consolidates the ~35-line ``getattr(args, "llm_*", default) or default`` blocks
that ``submit`` / ``train_and_submit`` / ``tune_and_submit`` in
``pipeline_handlers.py`` each previously built inline. Returns a dict keyed by
the exact ``llm_*`` parameter names accepted by
``level_5.run_submission_pipeline`` (and the level_6 result wrappers that
delegate to it), so handler call sites collapse to ``**arc_llm_kwargs_from_args(args)``.
"""

import argparse

from typing import Any


def arc_llm_kwargs_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Extract the 29 LLM-TTA kwargs that the submit-family pipelines accept.

    Behaviour-preserving: each field reproduces the exact ``getattr + or
    default`` fallback used by the inline handler code. Boolean flags use the
    ``bool(getattr(...))`` shape (no ``or`` fallback), matching the original.
    """
    return {
        "llm_execution_mode": str(getattr(args, "llm_execution_mode", "surrogate") or "surrogate"),
        "llm_num_augmentations": int(getattr(args, "llm_num_augmentations", 8) or 8),
        "llm_beam_width": int(getattr(args, "llm_beam_width", 12) or 12),
        "llm_max_candidates": int(getattr(args, "llm_max_candidates", 6) or 6),
        "llm_max_neg_log_score": float(getattr(args, "llm_max_neg_log_score", 120.0) or 120.0),
        "llm_seed": int(getattr(args, "llm_seed", 0) or 0),
        "llm_consistency_weight": float(getattr(args, "llm_consistency_weight", 1.0) or 1.0),
        "llm_model_weight": float(getattr(args, "llm_model_weight", 1.0) or 1.0),
        "llm_augmentation_likelihood_weight": float(
            getattr(args, "llm_augmentation_likelihood_weight", 1.0) or 1.0
        ),
        "llm_enable_neural_backend": bool(getattr(args, "llm_enable_neural_backend", False)),
        "llm_model_path": getattr(args, "llm_model_path", None),
        "llm_lora_path": getattr(args, "llm_lora_path", None),
        "llm_max_runtime_sec": float(getattr(args, "llm_max_runtime_sec", 0.0) or 0.0),
        "llm_task_runtime_sec": float(getattr(args, "llm_task_runtime_sec", 0.0) or 0.0),
        "llm_decode_runtime_sec": float(getattr(args, "llm_decode_runtime_sec", 0.0) or 0.0),
        "llm_adapt_steps": int(getattr(args, "llm_adapt_steps", 0) or 0),
        "llm_adapt_batch_size": int(getattr(args, "llm_adapt_batch_size", 1) or 1),
        "llm_adapt_gradient_accumulation_steps": int(
            getattr(args, "llm_adapt_gradient_accumulation_steps", 1) or 1
        ),
        "llm_adapt_disabled": bool(getattr(args, "llm_adapt_disabled", False)),
        "llm_per_task_adaptation": bool(getattr(args, "llm_per_task_adaptation", False)),
        "llm_runtime_attention_mode": str(
            getattr(args, "llm_runtime_attention_mode", "auto") or "auto"
        ),
        "llm_runtime_disable_compile": bool(getattr(args, "llm_runtime_disable_compile", False)),
        "llm_runtime_allocator_expandable_segments": bool(
            getattr(args, "llm_runtime_allocator_expandable_segments", True)
        ),
        "llm_runtime_allocator_max_split_size_mb": int(
            getattr(args, "llm_runtime_allocator_max_split_size_mb", 0) or 0
        ),
        "llm_prefer_cnn_attempt1": bool(getattr(args, "llm_prefer_cnn_attempt1", False)),
        "llm_candidate_ranker": str(
            getattr(args, "llm_candidate_ranker", "default") or "default"
        ),
        "llm_infer_artifact_dir": getattr(args, "llm_infer_artifact_dir", None),
        "llm_infer_artifact_run_name": str(
            getattr(args, "llm_infer_artifact_run_name", "") or ""
        ),
    }
