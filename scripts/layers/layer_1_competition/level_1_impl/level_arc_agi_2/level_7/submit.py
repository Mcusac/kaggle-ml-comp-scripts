"""Submit stage: build ``submission.json`` via heuristics / neural / LLM-TTA paths."""

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json_raw, save_json

from layers.layer_1_competition.level_0_infra.level_1 import (
    RunContext,
    build_submit_run_artifacts_patch,
    commit_run_artifacts,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ARC26PostProcessor,
    arc_find_first_existing_file,
    infer_finalize_artifact_root,
    stack_raise_if_unsupported_strategy,
    TEST_CHALLENGE_NAMES,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ARC26Paths,
    require_data_root,
    build_llm_tta_config,
    get_per_model_entry,
    resolve_chosen_params_for_submit,
    resolve_neural_paths_from_entry,
    second_attempt_grid,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    predict_grid_from_checkpoint,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.pipelines.score_submission import (
    log_local_evaluation_score_optional,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6 import (
    predict_attempts_for_submit_strategy,
)

_logger = get_logger(__name__)


def run_submission_pipeline(
    data_root: str,
    strategy: str,
    output_json: Optional[str] = None,
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
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
) -> Path:
    """Build submission.json using heuristics and/or neural checkpoint (primary model)."""
    out_path: Path | None = None
    root = require_data_root(data_root)

    models_list = [str(m) for m in models] if models else ["baseline_approx"]
    primary = models_list[0]

    stack_raise_if_unsupported_strategy(strategy)

    test_path = arc_find_first_existing_file(root, list(TEST_CHALLENGE_NAMES)) or (
        root / TEST_CHALLENGE_NAMES[0]
    )
    if not test_path.exists():
        raise FileNotFoundError(f"Missing ARC test challenges file: {test_path}")

    test_challenges = load_json_raw(test_path)
    if not isinstance(test_challenges, dict):
        raise ValueError("ARC test challenges JSON must be an object keyed by task id.")

    chosen_params = resolve_chosen_params_for_submit(
        tuned_config_path,
        train_metadata_json,
        primary,
    )

    entry = get_per_model_entry(train_metadata_json, primary)
    ckpt_path, cfg_path = resolve_neural_paths_from_entry(entry)
    if neural_checkpoint_path and str(neural_checkpoint_path).strip():
        ckpt_path = Path(str(neural_checkpoint_path).strip())
    if neural_train_config_path and str(neural_train_config_path).strip():
        cfg_path = Path(str(neural_train_config_path).strip())

    use_neural = (
        ckpt_path is not None
        and cfg_path is not None
        and ckpt_path.is_file()
        and cfg_path.is_file()
    )
    llm_cfg = build_llm_tta_config(
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
    strategy_telemetry: dict[str, int] = {}
    infer_artifact_final: dict[str, Any] | None = None

    try:
        submission: dict[str, list[dict[str, Any]]] = {}
        for task_id, task in test_challenges.items():
            tests = task.get("test", [])
            if not isinstance(tests, list):
                raise ValueError(f"Task {task_id!r} has invalid test list.")
            entries: list[dict[str, Any]] = []
            bound = len(tests) if max_targets <= 0 else min(len(tests), int(max_targets))
            for idx, pair in enumerate(tests):
                if idx >= bound:
                    input_grid = tests[0]["input"]
                else:
                    input_grid = pair["input"]
                use_strategy_path = (
                    str(strategy or "").strip().lower() == "llm_tta_dfs"
                    and not bool(llm_cfg.prefer_cnn_attempt1)
                )
                if use_neural and not use_strategy_path:
                    a1 = predict_grid_from_checkpoint(input_grid, ckpt_path, cfg_path)
                    a2 = second_attempt_grid(
                        input_grid,
                        strategy=strategy,
                        chosen_params=chosen_params,
                        data_root=str(root),
                        train_mode=str(train_mode),
                        max_pairs_per_task=int(max_targets or 0),
                    )
                else:
                    a1, a2, s_meta = predict_attempts_for_submit_strategy(
                        input_grid,
                        strategy=strategy,
                        chosen_params=chosen_params,
                        data_root=str(root),
                        train_mode=str(train_mode),
                        max_pairs_per_task=int(max_targets or 0),
                        task_payload=task if isinstance(task, dict) else None,
                        task_id=str(task_id),
                        test_index=int(idx),
                        llm_tta_config=llm_cfg,
                        return_metadata=True,
                    )
                    status = str(s_meta.get("status", "unknown"))
                    strategy_telemetry[status] = strategy_telemetry.get(status, 0) + 1
                entries.append({"attempt_1": a1, "attempt_2": a2})
            submission[str(task_id)] = entries

        submission = ARC26PostProcessor().normalize_submission(submission)
        out_path = Path(output_json) if output_json else ARC26Paths().submission_output_path()
        save_json(submission, out_path)
        log_local_evaluation_score_optional(data_root=str(root), submission_path=str(out_path))
        if str(strategy or "").strip().lower() == "llm_tta_dfs" and str(
            llm_cfg.infer_artifact_dir or ""
        ).strip():
            try:
                infer_artifact_final = infer_finalize_artifact_root(
                    str(llm_cfg.infer_artifact_dir).strip(),
                    run_name=str(llm_cfg.infer_artifact_run_name or ""),
                )
                _logger.info(
                    "✅ inference decoded_results materialized: %s",
                    infer_artifact_final.get("decoded_store_pkl"),
                )
            except Exception as e:
                _logger.warning("⚠️ infer_finalize_artifact_root failed: %s", e)
        _logger.info(
            "Wrote ARC submission (%s strategy, primary_model=%s, neural=%s): %s",
            strategy,
            primary,
            use_neural,
            out_path,
        )
        return out_path
    finally:
        if run_ctx is not None and out_path is not None and out_path.is_file():
            patch = build_submit_run_artifacts_patch(
                strategy=str(strategy),
                max_targets=int(max_targets),
                models_list=models_list,
                primary_model=primary,
                use_neural=use_neural,
                llm_cfg=llm_cfg,
                infer_artifact_final=infer_artifact_final,
                strategy_telemetry=strategy_telemetry,
                tuned_config_path=str(tuned_config_path) if tuned_config_path else None,
                train_metadata_json=str(train_metadata_json) if train_metadata_json else None,
                data_root=str(root),
                submission_json_src=str(out_path),
            )
            commit_run_artifacts(
                run_ctx,
                patch,
                src_path=out_path,
                dest_name="submission.json",
            )
