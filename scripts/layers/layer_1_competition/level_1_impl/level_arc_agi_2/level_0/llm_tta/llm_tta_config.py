"""LLM-TTA DFS configuration dataclass and validation."""

import math

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmTtaDfsConfig:
    """Runtime parameters for the ``llm_tta_dfs`` strategy."""

    execution_mode: str = "surrogate"  # surrogate|lm_backend
    num_augmentations: int = 8
    beam_width: int = 12
    max_candidates: int = 6
    max_neg_log_score: float = 120.0
    seed: int = 0
    consistency_weight: float = 1.0
    model_weight: float = 1.0
    augmentation_likelihood_weight: float = 1.0
    enable_neural_backend: bool = False  # retained for backward compatibility
    model_path: str | None = None
    lora_path: str | None = None
    max_runtime_sec: float = 0.0
    task_runtime_sec: float = 0.0
    decode_runtime_sec: float = 0.0
    adapt_steps: int = 0
    adapt_batch_size: int = 1
    adapt_gradient_accumulation_steps: int = 1
    adapt_disabled: bool = False
    per_task_adaptation: bool = False
    runtime_attention_mode: str = "auto"  # auto|eager|sdpa
    runtime_disable_compile: bool = False
    runtime_allocator_expandable_segments: bool = True
    runtime_allocator_max_split_size_mb: int = 0
    prefer_cnn_attempt1: bool = False
    candidate_ranker: str = "default"
    turbo_prune_max_nll: float = -math.log(0.2)
    turbo_max_new_tokens: int | None = None
    turbo_inner_loop_wall_sec: float | None = None
    infer_artifact_dir: str | None = None
    infer_artifact_run_name: str = ""


def validate_llm_tta_dfs_config(config: LlmTtaDfsConfig) -> None:
    """Raise ``ValueError`` for incompatible field combinations."""
    mode = str(config.execution_mode or "").strip().lower()
    if mode not in ("surrogate", "lm_backend"):
        raise ValueError(
            f"Invalid llm_tta execution_mode={config.execution_mode!r}. Use surrogate|lm_backend."
        )
    if mode == "surrogate":
        lm_fields_set = (
            bool(config.model_path)
            or bool(config.lora_path)
            or bool(config.enable_neural_backend)
            or bool(config.per_task_adaptation)
        )
        if lm_fields_set:
            raise ValueError(
                "LM-only options were provided in surrogate mode. "
                "Set execution_mode='lm_backend' to use model_path/lora_path."
            )
    if mode == "lm_backend" and not str(config.model_path or "").strip():
        raise ValueError("execution_mode='lm_backend' requires llm_model_path.")
    if bool(config.per_task_adaptation):
        if mode != "lm_backend":
            raise ValueError("per_task_adaptation requires execution_mode='lm_backend'.")
        if bool(config.adapt_disabled):
            raise ValueError("per_task_adaptation cannot be used with adapt_disabled=True.")
        if int(config.adapt_steps or 0) < 1:
            raise ValueError("per_task_adaptation requires adapt_steps >= 1.")
    cr = str(config.candidate_ranker or "default").strip().lower()
    if cr not in ("default", "kgmon", "probmul"):
        raise ValueError(
            f"Invalid candidate_ranker={config.candidate_ranker!r}. Use default|kgmon|probmul."
        )
