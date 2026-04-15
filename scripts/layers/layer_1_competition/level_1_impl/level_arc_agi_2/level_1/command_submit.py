"""Submit command builder."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import append_common_args, CONTEST, append_llm_args


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

    # LLM args
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

    cmd = build_run_py_base_command(CONTEST, "submit", data_root)

    cmd.extend(["--strategy", str(strategy)])
    cmd.extend(["--models", ",".join(model_names)])

    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])

    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])

    if ensemble_weights:
        cmd.extend(
            ["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)]
        )

    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")

    if tuned_config_path:
        cmd.extend(["--tuned-config", str(tuned_config_path)])

    append_common_args(cmd, run_id, run_dir, log_file)

    append_llm_args(
        cmd,
        strategy,
        llm_execution_mode,
        llm_num_augmentations,
        llm_beam_width,
        llm_max_candidates,
        llm_max_neg_log_score,
        llm_seed,
        llm_consistency_weight,
        llm_model_weight,
        llm_enable_neural_backend,
        llm_model_path,
        llm_lora_path,
        llm_max_runtime_sec,
        llm_task_runtime_sec,
        llm_decode_runtime_sec,
        llm_adapt_steps,
        llm_adapt_batch_size,
        llm_adapt_gradient_accumulation_steps,
        llm_adapt_disabled,
        llm_per_task_adaptation,
        llm_augmentation_likelihood_weight,
        llm_runtime_attention_mode,
        llm_runtime_disable_compile,
        llm_runtime_allocator_expandable_segments,
        llm_runtime_allocator_max_split_size_mb,
        llm_prefer_cnn_attempt1,
        llm_infer_artifact_dir,
        llm_infer_artifact_run_name,
    )

    return cmd