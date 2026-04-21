"""Contest-agnostic argv token appenders shared by contest command builders.

These primitives centralise the notebook-cell and ``python run.py`` argv
shapes that contest packages build. Each helper mutates ``cmd`` in place and
appends argv tokens in a fixed, byte-stable order so both shapes can share
them without altering their output ordering.
"""

import argparse

from typing import Any, List, Optional


def resolve_models(
    models: Optional[List[str]],
    default: Optional[List[str]] = None,
) -> List[str]:
    """Return ``models`` when non-empty, else ``default`` or ``["baseline_approx"]``."""
    return models or (default if default is not None else ["baseline_approx"])


def append_models(cmd: List[str], models: List[str]) -> None:
    """Append ``--models a,b,c``."""
    cmd.extend(["--models", ",".join(models)])


def resolve_and_append_models(
    cmd: List[str],
    models: Optional[List[str]],
    default: Optional[List[str]] = None,
) -> None:
    """Append the resolved models list."""
    append_models(cmd, resolve_models(models, default))


def append_strategy(cmd: List[str], strategy: str) -> None:
    """Append ``--strategy S``."""
    cmd.extend(["--strategy", str(strategy)])


def append_train_mode(cmd: List[str], train_mode: str) -> None:
    """Append ``--train-mode M``."""
    cmd.extend(["--train-mode", str(train_mode)])


def append_tune_args(cmd: List[str], model: str, search_type: str) -> None:
    """Append ``--model M --search-type T`` (paired, like the notebook builder)."""
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])


def append_max_targets(cmd: List[str], max_targets: int) -> None:
    """Append ``--max-targets N`` when ``N > 0``."""
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])


def append_output_csv(cmd: List[str], output_csv: Optional[str]) -> None:
    """Append ``--output-csv P`` when set."""
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])


def append_ensemble_weights(
    cmd: List[str],
    ensemble_weights: Optional[List[float]],
) -> None:
    """Append ``--ensemble-weights w1,w2,...`` when set."""
    if ensemble_weights:
        cmd.extend(
            [
                "--ensemble-weights",
                ",".join(str(v) for v in ensemble_weights),
            ]
        )


def append_no_validation_stacking(
    cmd: List[str],
    use_validation_for_stacking: bool,
) -> None:
    """Append ``--no-validation-stacking`` when validation-based stacking is disabled."""
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")


def append_tuned_config(cmd: List[str], tuned_config_path: Optional[str]) -> None:
    """Append ``--tuned-config P`` when set."""
    if tuned_config_path:
        cmd.extend(["--tuned-config", str(tuned_config_path)])


def append_run_args(
    cmd: List[str],
    run_id: Optional[str],
    run_dir: Optional[str],
    log_file: Optional[str],
) -> None:
    """Append ``--run-id``, ``--run-dir``, ``--log-file`` when set (in that order)."""
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])


def append_llm_args(
    cmd: List[str],
    strategy: str,
    llm_execution_mode: str,
    llm_num_augmentations: int,
    llm_beam_width: int,
    llm_max_candidates: int,
    llm_max_neg_log_score: float,
    llm_seed: int,
    llm_consistency_weight: float,
    llm_model_weight: float,
    llm_enable_neural_backend: bool,
    llm_model_path: Optional[str],
    llm_lora_path: Optional[str],
    llm_max_runtime_sec: float,
    llm_task_runtime_sec: float,
    llm_decode_runtime_sec: float,
    llm_adapt_steps: int,
    llm_adapt_batch_size: int,
    llm_adapt_gradient_accumulation_steps: int,
    llm_adapt_disabled: bool,
    llm_per_task_adaptation: bool,
    llm_augmentation_likelihood_weight: float,
    llm_runtime_attention_mode: str,
    llm_runtime_disable_compile: bool,
    llm_runtime_allocator_expandable_segments: bool,
    llm_runtime_allocator_max_split_size_mb: int,
    llm_prefer_cnn_attempt1: bool,
    llm_infer_artifact_dir: Optional[str],
    llm_infer_artifact_run_name: str,
) -> None:
    """Append LLM-TTA DFS argv tokens when ``strategy == llm_tta_dfs``."""
    if str(strategy).strip().lower() != "llm_tta_dfs":
        return

    cmd.extend(["--llm-execution-mode", str(llm_execution_mode)])
    cmd.extend(["--llm-num-augmentations", str(int(llm_num_augmentations))])
    cmd.extend(["--llm-beam-width", str(int(llm_beam_width))])
    cmd.extend(["--llm-max-candidates", str(int(llm_max_candidates))])
    cmd.extend(["--llm-max-neg-log-score", str(float(llm_max_neg_log_score))])
    cmd.extend(["--llm-seed", str(int(llm_seed))])
    cmd.extend(["--llm-consistency-weight", str(float(llm_consistency_weight))])
    cmd.extend(["--llm-model-weight", str(float(llm_model_weight))])
    cmd.extend(
        ["--llm-augmentation-likelihood-weight", str(float(llm_augmentation_likelihood_weight))]
    )

    if llm_enable_neural_backend:
        cmd.append("--llm-enable-neural-backend")

    if llm_model_path:
        cmd.extend(["--llm-model-path", str(llm_model_path)])

    if llm_lora_path:
        cmd.extend(["--llm-lora-path", str(llm_lora_path)])

    if float(llm_max_runtime_sec) > 0:
        cmd.extend(["--llm-max-runtime-sec", str(float(llm_max_runtime_sec))])

    if float(llm_task_runtime_sec) > 0:
        cmd.extend(["--llm-task-runtime-sec", str(float(llm_task_runtime_sec))])

    if float(llm_decode_runtime_sec) > 0:
        cmd.extend(["--llm-decode-runtime-sec", str(float(llm_decode_runtime_sec))])

    if int(llm_adapt_steps) > 0:
        cmd.extend(["--llm-adapt-steps", str(int(llm_adapt_steps))])

    cmd.extend(["--llm-adapt-batch-size", str(int(llm_adapt_batch_size))])

    cmd.extend(
        [
            "--llm-adapt-gradient-accumulation-steps",
            str(int(llm_adapt_gradient_accumulation_steps)),
        ]
    )

    if llm_adapt_disabled:
        cmd.append("--llm-adapt-disabled")

    if llm_per_task_adaptation:
        cmd.append("--llm-per-task-adaptation")

    cmd.extend(["--llm-runtime-attention-mode", str(llm_runtime_attention_mode)])

    if llm_runtime_disable_compile:
        cmd.append("--llm-runtime-disable-compile")

    if llm_runtime_allocator_expandable_segments:
        cmd.append("--llm-runtime-allocator-expandable-segments")

    if int(llm_runtime_allocator_max_split_size_mb) > 0:
        cmd.extend(
            [
                "--llm-runtime-allocator-max-split-size-mb",
                str(int(llm_runtime_allocator_max_split_size_mb)),
            ]
        )

    if llm_prefer_cnn_attempt1:
        cmd.append("--llm-prefer-cnn-attempt1")

    if llm_infer_artifact_dir:
        cmd.extend(["--llm-infer-artifact-dir", str(llm_infer_artifact_dir)])

    if llm_infer_artifact_run_name:
        cmd.extend(["--llm-infer-artifact-run-name", str(llm_infer_artifact_run_name)])


def llm_tta_kwargs_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Extract LLM-TTA kwargs dict for submit-family pipelines (``llm_*`` keys)."""
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