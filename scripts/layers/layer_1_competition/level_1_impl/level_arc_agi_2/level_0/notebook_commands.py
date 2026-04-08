"""ARC notebook command builders."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

_CONTEST = "arc_agi_2"


def build_validate_data_command(
    data_root: Optional[str] = None,
    max_targets: int = 0,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = build_run_py_base_command(_CONTEST, "validate_data", data_root)
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_train_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "train", data_root)
    cmd.extend(["--train-mode", str(train_mode), "--models", ",".join(model_names)])
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_tune_command(
    data_root: Optional[str] = None,
    model: str = "baseline_approx",
    search_type: str = "quick",
    max_targets: int = 0,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = build_run_py_base_command(_CONTEST, "tune", data_root)
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_submit_command(
    data_root: Optional[str] = None,
    strategy: str = "single",
    models: Optional[List[str]] = None,
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    tuned_config_path: Optional[str] = None,
    llm_execution_mode: str = "surrogate",
    llm_num_augmentations: int = 8,
    llm_beam_width: int = 12,
    llm_max_candidates: int = 6,
    llm_max_neg_log_score: float = 120.0,
    llm_seed: int = 0,
    llm_consistency_weight: float = 1.0,
    llm_model_weight: float = 1.0,
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
    llm_augmentation_likelihood_weight: float = 1.0,
    llm_runtime_attention_mode: str = "auto",
    llm_runtime_disable_compile: bool = False,
    llm_runtime_allocator_expandable_segments: bool = True,
    llm_runtime_allocator_max_split_size_mb: int = 0,
    llm_prefer_cnn_attempt1: bool = False,
    llm_infer_artifact_dir: Optional[str] = None,
    llm_infer_artifact_run_name: str = "",
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "submit", data_root)
    cmd.extend(["--strategy", str(strategy), "--models", ",".join(model_names)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if tuned_config_path:
        cmd.extend(["--tuned-config", str(tuned_config_path)])
    if str(strategy).strip().lower() == "llm_tta_dfs":
        cmd.extend(["--llm-execution-mode", str(llm_execution_mode or "surrogate")])
        cmd.extend(["--llm-num-augmentations", str(int(llm_num_augmentations or 8))])
        cmd.extend(["--llm-beam-width", str(int(llm_beam_width or 12))])
        cmd.extend(["--llm-max-candidates", str(int(llm_max_candidates or 6))])
        cmd.extend(["--llm-max-neg-log-score", str(float(llm_max_neg_log_score or 120.0))])
        cmd.extend(["--llm-seed", str(int(llm_seed or 0))])
        cmd.extend(["--llm-consistency-weight", str(float(llm_consistency_weight))])
        cmd.extend(["--llm-model-weight", str(float(llm_model_weight))])
        cmd.extend(["--llm-augmentation-likelihood-weight", str(float(llm_augmentation_likelihood_weight))])
        if llm_enable_neural_backend:
            cmd.append("--llm-enable-neural-backend")
        if llm_model_path:
            cmd.extend(["--llm-model-path", str(llm_model_path)])
        if llm_lora_path:
            cmd.extend(["--llm-lora-path", str(llm_lora_path)])
        if float(llm_max_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-max-runtime-sec", str(float(llm_max_runtime_sec))])
        if float(llm_task_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-task-runtime-sec", str(float(llm_task_runtime_sec))])
        if float(llm_decode_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-decode-runtime-sec", str(float(llm_decode_runtime_sec))])
        if int(llm_adapt_steps or 0) > 0:
            cmd.extend(["--llm-adapt-steps", str(int(llm_adapt_steps))])
        cmd.extend(["--llm-adapt-batch-size", str(int(llm_adapt_batch_size or 1))])
        cmd.extend(
            [
                "--llm-adapt-gradient-accumulation-steps",
                str(int(llm_adapt_gradient_accumulation_steps or 1)),
            ]
        )
        if llm_adapt_disabled:
            cmd.append("--llm-adapt-disabled")
        if llm_per_task_adaptation:
            cmd.append("--llm-per-task-adaptation")
        cmd.extend(["--llm-runtime-attention-mode", str(llm_runtime_attention_mode or "auto")])
        if llm_runtime_disable_compile:
            cmd.append("--llm-runtime-disable-compile")
        if llm_runtime_allocator_expandable_segments:
            cmd.append("--llm-runtime-allocator-expandable-segments")
        if int(llm_runtime_allocator_max_split_size_mb or 0) > 0:
            cmd.extend(
                ["--llm-runtime-allocator-max-split-size-mb", str(int(llm_runtime_allocator_max_split_size_mb))]
            )
        if llm_prefer_cnn_attempt1:
            cmd.append("--llm-prefer-cnn-attempt1")
        if llm_infer_artifact_dir and str(llm_infer_artifact_dir).strip():
            cmd.extend(["--llm-infer-artifact-dir", str(llm_infer_artifact_dir).strip()])
        if str(llm_infer_artifact_run_name or "").strip():
            cmd.extend(["--llm-infer-artifact-run-name", str(llm_infer_artifact_run_name).strip()])
    return cmd


def build_train_and_submit_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    strategy: str = "single",
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    llm_execution_mode: str = "surrogate",
    llm_num_augmentations: int = 8,
    llm_beam_width: int = 12,
    llm_max_candidates: int = 6,
    llm_max_neg_log_score: float = 120.0,
    llm_seed: int = 0,
    llm_consistency_weight: float = 1.0,
    llm_model_weight: float = 1.0,
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
    llm_augmentation_likelihood_weight: float = 1.0,
    llm_runtime_attention_mode: str = "auto",
    llm_runtime_disable_compile: bool = False,
    llm_runtime_allocator_expandable_segments: bool = True,
    llm_runtime_allocator_max_split_size_mb: int = 0,
    llm_prefer_cnn_attempt1: bool = False,
    llm_infer_artifact_dir: Optional[str] = None,
    llm_infer_artifact_run_name: str = "",
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "train_and_submit", data_root)
    cmd.extend(["--train-mode", str(train_mode), "--models", ",".join(model_names)])
    cmd.extend(["--strategy", str(strategy)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if str(strategy).strip().lower() == "llm_tta_dfs":
        cmd.extend(["--llm-execution-mode", str(llm_execution_mode or "surrogate")])
        cmd.extend(["--llm-num-augmentations", str(int(llm_num_augmentations or 8))])
        cmd.extend(["--llm-beam-width", str(int(llm_beam_width or 12))])
        cmd.extend(["--llm-max-candidates", str(int(llm_max_candidates or 6))])
        cmd.extend(["--llm-max-neg-log-score", str(float(llm_max_neg_log_score or 120.0))])
        cmd.extend(["--llm-seed", str(int(llm_seed or 0))])
        cmd.extend(["--llm-consistency-weight", str(float(llm_consistency_weight))])
        cmd.extend(["--llm-model-weight", str(float(llm_model_weight))])
        cmd.extend(["--llm-augmentation-likelihood-weight", str(float(llm_augmentation_likelihood_weight))])
        if llm_enable_neural_backend:
            cmd.append("--llm-enable-neural-backend")
        if llm_model_path:
            cmd.extend(["--llm-model-path", str(llm_model_path)])
        if llm_lora_path:
            cmd.extend(["--llm-lora-path", str(llm_lora_path)])
        if float(llm_max_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-max-runtime-sec", str(float(llm_max_runtime_sec))])
        if float(llm_task_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-task-runtime-sec", str(float(llm_task_runtime_sec))])
        if float(llm_decode_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-decode-runtime-sec", str(float(llm_decode_runtime_sec))])
        if int(llm_adapt_steps or 0) > 0:
            cmd.extend(["--llm-adapt-steps", str(int(llm_adapt_steps))])
        cmd.extend(["--llm-adapt-batch-size", str(int(llm_adapt_batch_size or 1))])
        cmd.extend(
            [
                "--llm-adapt-gradient-accumulation-steps",
                str(int(llm_adapt_gradient_accumulation_steps or 1)),
            ]
        )
        if llm_adapt_disabled:
            cmd.append("--llm-adapt-disabled")
        if llm_per_task_adaptation:
            cmd.append("--llm-per-task-adaptation")
        cmd.extend(["--llm-runtime-attention-mode", str(llm_runtime_attention_mode or "auto")])
        if llm_runtime_disable_compile:
            cmd.append("--llm-runtime-disable-compile")
        if llm_runtime_allocator_expandable_segments:
            cmd.append("--llm-runtime-allocator-expandable-segments")
        if int(llm_runtime_allocator_max_split_size_mb or 0) > 0:
            cmd.extend(
                ["--llm-runtime-allocator-max-split-size-mb", str(int(llm_runtime_allocator_max_split_size_mb))]
            )
        if llm_prefer_cnn_attempt1:
            cmd.append("--llm-prefer-cnn-attempt1")
        if llm_infer_artifact_dir and str(llm_infer_artifact_dir).strip():
            cmd.extend(["--llm-infer-artifact-dir", str(llm_infer_artifact_dir).strip()])
        if str(llm_infer_artifact_run_name or "").strip():
            cmd.extend(["--llm-infer-artifact-run-name", str(llm_infer_artifact_run_name).strip()])
    return cmd


def build_tune_and_submit_command(
    data_root: Optional[str] = None,
    model: str = "baseline_approx",
    search_type: str = "quick",
    strategy: str = "single",
    models: Optional[List[str]] = None,
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    llm_execution_mode: str = "surrogate",
    llm_num_augmentations: int = 8,
    llm_beam_width: int = 12,
    llm_max_candidates: int = 6,
    llm_max_neg_log_score: float = 120.0,
    llm_seed: int = 0,
    llm_consistency_weight: float = 1.0,
    llm_model_weight: float = 1.0,
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
    llm_augmentation_likelihood_weight: float = 1.0,
    llm_runtime_attention_mode: str = "auto",
    llm_runtime_disable_compile: bool = False,
    llm_runtime_allocator_expandable_segments: bool = True,
    llm_runtime_allocator_max_split_size_mb: int = 0,
    llm_prefer_cnn_attempt1: bool = False,
    llm_infer_artifact_dir: Optional[str] = None,
    llm_infer_artifact_run_name: str = "",
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "tune_and_submit", data_root)
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])
    cmd.extend(["--strategy", str(strategy), "--models", ",".join(model_names)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if str(strategy).strip().lower() == "llm_tta_dfs":
        cmd.extend(["--llm-execution-mode", str(llm_execution_mode or "surrogate")])
        cmd.extend(["--llm-num-augmentations", str(int(llm_num_augmentations or 8))])
        cmd.extend(["--llm-beam-width", str(int(llm_beam_width or 12))])
        cmd.extend(["--llm-max-candidates", str(int(llm_max_candidates or 6))])
        cmd.extend(["--llm-max-neg-log-score", str(float(llm_max_neg_log_score or 120.0))])
        cmd.extend(["--llm-seed", str(int(llm_seed or 0))])
        cmd.extend(["--llm-consistency-weight", str(float(llm_consistency_weight))])
        cmd.extend(["--llm-model-weight", str(float(llm_model_weight))])
        cmd.extend(["--llm-augmentation-likelihood-weight", str(float(llm_augmentation_likelihood_weight))])
        if llm_enable_neural_backend:
            cmd.append("--llm-enable-neural-backend")
        if llm_model_path:
            cmd.extend(["--llm-model-path", str(llm_model_path)])
        if llm_lora_path:
            cmd.extend(["--llm-lora-path", str(llm_lora_path)])
        if float(llm_max_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-max-runtime-sec", str(float(llm_max_runtime_sec))])
        if float(llm_task_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-task-runtime-sec", str(float(llm_task_runtime_sec))])
        if float(llm_decode_runtime_sec or 0.0) > 0.0:
            cmd.extend(["--llm-decode-runtime-sec", str(float(llm_decode_runtime_sec))])
        if int(llm_adapt_steps or 0) > 0:
            cmd.extend(["--llm-adapt-steps", str(int(llm_adapt_steps))])
        cmd.extend(["--llm-adapt-batch-size", str(int(llm_adapt_batch_size or 1))])
        cmd.extend(
            [
                "--llm-adapt-gradient-accumulation-steps",
                str(int(llm_adapt_gradient_accumulation_steps or 1)),
            ]
        )
        if llm_adapt_disabled:
            cmd.append("--llm-adapt-disabled")
        if llm_per_task_adaptation:
            cmd.append("--llm-per-task-adaptation")
        cmd.extend(["--llm-runtime-attention-mode", str(llm_runtime_attention_mode or "auto")])
        if llm_runtime_disable_compile:
            cmd.append("--llm-runtime-disable-compile")
        if llm_runtime_allocator_expandable_segments:
            cmd.append("--llm-runtime-allocator-expandable-segments")
        if int(llm_runtime_allocator_max_split_size_mb or 0) > 0:
            cmd.extend(
                ["--llm-runtime-allocator-max-split-size-mb", str(int(llm_runtime_allocator_max_split_size_mb))]
            )
        if llm_prefer_cnn_attempt1:
            cmd.append("--llm-prefer-cnn-attempt1")
        if llm_infer_artifact_dir and str(llm_infer_artifact_dir).strip():
            cmd.extend(["--llm-infer-artifact-dir", str(llm_infer_artifact_dir).strip()])
        if str(llm_infer_artifact_run_name or "").strip():
            cmd.extend(["--llm-infer-artifact-run-name", str(llm_infer_artifact_run_name).strip()])
    return cmd

