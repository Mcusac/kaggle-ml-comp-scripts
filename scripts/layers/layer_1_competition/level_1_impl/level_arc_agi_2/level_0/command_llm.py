"""LLM command argument builder."""

from typing import List, Optional


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