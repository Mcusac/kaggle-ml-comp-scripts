"""Path-returning ARC pipeline stages (train / tune / submit)."""

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger

from layers.layer_1_competition.level_0_infra.level_0.artifacts import read_json, write_json
from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ARC26Paths,
    ARC26PostProcessor,
    DEFAULT_SUBMIT_HEURISTIC,
    heuristic_order_for_train_mode,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
    read_submit_max_tasks_env,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    load_chosen_params_from_tuned_config,
    rank_heuristics_on_training,
    select_best_heuristic,
    select_best_heuristic_on_training,
    update_run_metadata,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    LlmTtaDfsConfig,
    predict_grid_from_checkpoint,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_stack_policy import (
    stack_raise_if_unsupported_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    get_trainer,
    list_available_models,
    predict_attempts_for_submit_strategy,
    score_neural_on_evaluation,
)

logger = get_logger(__name__)

def _default_chosen_params() -> dict[str, Any]:
    return {"heuristic": DEFAULT_SUBMIT_HEURISTIC, "version": 1}


def _resolve_chosen_params_for_submit(
    tuned_config_path: Optional[str],
    train_metadata_json: Optional[str],
    primary_model: str,
) -> dict[str, Any] | None:
    if tuned_config_path and str(tuned_config_path).strip():
        cp = load_chosen_params_from_tuned_config(str(tuned_config_path))
        if cp:
            return cp
    if train_metadata_json and str(train_metadata_json).strip():
        p = Path(str(train_metadata_json).strip())
        if p.is_file():
            try:
                data = read_json(p)
                if isinstance(data, dict):
                    if isinstance(data.get("chosen_params"), dict):
                        return dict(data["chosen_params"])
                    pm = data.get("per_model")
                    if isinstance(pm, dict):
                        entry = pm.get(str(primary_model))
                        if isinstance(entry, dict) and isinstance(entry.get("chosen_params"), dict):
                            return dict(entry["chosen_params"])
                    models = data.get("models")
                    if isinstance(models, list) and models and isinstance(pm, dict):
                        first = str(models[0])
                        entry = pm.get(first)
                        if isinstance(entry, dict) and isinstance(entry.get("chosen_params"), dict):
                            return dict(entry["chosen_params"])
            except Exception as e:
                logger.warning("Could not read train metadata for submit chosen_params: %s", e)
    return None


def _get_per_model_entry(train_metadata_json: Optional[str], model_name: str) -> dict[str, Any] | None:
    if not train_metadata_json or not str(train_metadata_json).strip():
        return None
    p = Path(str(train_metadata_json).strip())
    if not p.is_file():
        return None
    try:
        data = read_json(p)
        if not isinstance(data, dict):
            return None
        pm = data.get("per_model")
        if isinstance(pm, dict):
            entry = pm.get(str(model_name))
            if isinstance(entry, dict):
                return entry
    except Exception as e:
        logger.warning("Could not read per_model from train metadata: %s", e)
    return None


def _resolve_neural_paths_from_entry(entry: dict[str, Any] | None) -> tuple[Path | None, Path | None]:
    if not entry:
        return None, None
    art = entry.get("artifacts")
    if not isinstance(art, dict):
        return None, None
    ckpt = art.get("checkpoint")
    cfg = art.get("train_config")
    if not ckpt or not cfg:
        return None, None
    cp = Path(str(ckpt))
    tp = Path(str(cfg))
    if cp.is_file() and tp.is_file():
        return cp, tp
    return None, None


def _second_attempt_grid(
    input_grid: list[list[int]],
    *,
    strategy: str,
    chosen_params: dict[str, Any] | None,
    data_root: str,
    train_mode: str,
    max_pairs_per_task: int,
) -> list[list[int]]:
    s = str(strategy or "").lower()
    if s == "ensemble":
        order = heuristic_order_for_train_mode(train_mode)
        ranked = rank_heuristics_on_training(
            data_root,
            order,
            max_tasks=read_submit_max_tasks_env() or 0,
            max_pairs_per_task=int(max_pairs_per_task or 0),
        )
        if len(ranked) > 1:
            h2 = ranked[1][0]
            _, a2 = predict_attempts_for_heuristic(input_grid, h2)
            return a2
        if ranked:
            h = ranked[0][0]
            _, a2 = predict_attempts_for_heuristic(input_grid, h)
            return a2
    _, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
    return a2


def _build_llm_tta_config(
    *,
    llm_execution_mode: str = "surrogate",
    llm_num_augmentations: int = 8,
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
    llm_runtime_attention_mode: str = "auto",
    llm_runtime_disable_compile: bool = False,
    llm_runtime_allocator_expandable_segments: bool = True,
    llm_runtime_allocator_max_split_size_mb: int = 0,
    llm_prefer_cnn_attempt1: bool = False,
    llm_candidate_ranker: str = "default",
) -> LlmTtaDfsConfig:
    return LlmTtaDfsConfig(
        execution_mode=str(llm_execution_mode or "surrogate"),
        num_augmentations=int(llm_num_augmentations or 1),
        beam_width=int(llm_beam_width or 1),
        max_candidates=int(llm_max_candidates or 1),
        max_neg_log_score=float(llm_max_neg_log_score or 120.0),
        seed=int(llm_seed or 0),
        consistency_weight=float(llm_consistency_weight),
        model_weight=float(llm_model_weight),
        augmentation_likelihood_weight=float(llm_augmentation_likelihood_weight),
        enable_neural_backend=bool(llm_enable_neural_backend),
        model_path=(str(llm_model_path).strip() if llm_model_path else None),
        lora_path=(str(llm_lora_path).strip() if llm_lora_path else None),
        max_runtime_sec=float(llm_max_runtime_sec or 0.0),
        task_runtime_sec=float(llm_task_runtime_sec or 0.0),
        decode_runtime_sec=float(llm_decode_runtime_sec or 0.0),
        adapt_steps=int(llm_adapt_steps or 0),
        adapt_batch_size=max(1, int(llm_adapt_batch_size or 1)),
        adapt_gradient_accumulation_steps=max(1, int(llm_adapt_gradient_accumulation_steps or 1)),
        adapt_disabled=bool(llm_adapt_disabled),
        runtime_attention_mode=str(llm_runtime_attention_mode or "auto"),
        runtime_disable_compile=bool(llm_runtime_disable_compile),
        runtime_allocator_expandable_segments=bool(llm_runtime_allocator_expandable_segments),
        runtime_allocator_max_split_size_mb=int(llm_runtime_allocator_max_split_size_mb or 0),
        prefer_cnn_attempt1=bool(llm_prefer_cnn_attempt1),
        candidate_ranker=str(llm_candidate_ranker or "default"),
    )


def run_train_pipeline(
    data_root: str,
    train_mode: str,
    models: list[str],
    run_ctx: Optional[RunContext] = None,
    max_targets: int = 0,
) -> Path:
    """Train registered models (e.g. grid_cnn_v0); for others pick heuristics on training JSON."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    out_dir = contest_models_dir(ARC26Paths(), "arc_agi_2")
    ensure_dir(out_dir)
    metadata_path = out_dir / "train_metadata.json"

    per_model: dict[str, Any] = {}
    registered = list_available_models()

    for m in models:
        name = str(m)
        trainer = get_trainer(name)
        if trainer is not None:
            model_output_dir = out_dir / name
            ensure_dir(model_output_dir)
            logger.info("Training registered model %s -> %s", name, model_output_dir)
            trainer(str(root), str(model_output_dir))
            ckpt = model_output_dir / "model.pt"
            tcfg = model_output_dir / "train_config.json"
            per_model[name] = {
                "chosen_params": _default_chosen_params(),
                "artifacts": {
                    "model_type": name,
                    "checkpoint": str(ckpt),
                    "train_config": str(tcfg),
                },
            }
        else:
            chosen_params, train_scores = select_best_heuristic_on_training(
                str(root),
                str(train_mode),
                max_targets=int(max_targets or 0),
            )
            per_model[name] = {"chosen_params": chosen_params, "train_scores": train_scores}
            if name in registered:
                logger.warning("Model %r is in registry but get_trainer returned None", name)

    metadata = {
        "contest": "arc_agi_2",
        "train_mode": str(train_mode),
        "models": [str(m) for m in models],
        "registered_neural_models": registered,
        "data_root": str(root),
        "status": "complete",
        "per_model": per_model,
    }
    write_json(metadata_path, metadata)
    logger.info("Wrote ARC training metadata: %s", metadata_path)
    if run_ctx is not None:
        try:
            update_run_metadata(
                run_ctx,
                {
                    "config": {"train": {"train_mode": str(train_mode), "models": [str(m) for m in models]}},
                    "inputs": {"data_root": str(root)},
                    "artifacts": {"train_metadata_json_src": str(metadata_path)},
                },
            )
            copy_artifact_into_run(run_ctx, src=metadata_path, dest_name="train_metadata.json")
            finalize_run_success(run_ctx)
        except Exception as e:
            finalize_run_failure(run_ctx, e)
    return metadata_path


def run_tune_pipeline(
    data_root: str,
    model_name: str,
    search_type: str = "quick",
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    train_metadata_json: Optional[str] = None,
) -> Path:
    """Select best baseline heuristic using evaluation tasks when solutions exist."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    out_dir = contest_models_dir(ARC26Paths(), "arc_agi_2") / str(model_name)
    ensure_dir(out_dir)
    tune_path = out_dir / "best_config.json"
    chosen_params, tune_scores = select_best_heuristic(
        str(root),
        str(search_type),
        max_targets=int(max_targets or 0),
    )
    metadata_hint = train_metadata_json
    if not metadata_hint:
        candidate = contest_models_dir(ARC26Paths(), "arc_agi_2") / "train_metadata.json"
        if candidate.is_file():
            metadata_hint = str(candidate)

    neural_eval_exact_match: float | None = None
    entry = _get_per_model_entry(metadata_hint, str(model_name))
    ckpt_path, cfg_path = _resolve_neural_paths_from_entry(entry)
    if ckpt_path is not None and cfg_path is not None:
        neural_eval_exact_match = score_neural_on_evaluation(
            str(root),
            str(ckpt_path),
            str(cfg_path),
            max_tasks=read_submit_max_tasks_env() or 0,
            max_targets=int(max_targets or 0),
        )

    result = {
        "model_name": str(model_name),
        "search_type": str(search_type),
        "max_targets": int(max_targets),
        "chosen_params": chosen_params,
        "tune_scores": tune_scores,
    }
    if neural_eval_exact_match is not None:
        result["neural_eval_exact_match"] = float(neural_eval_exact_match)
    write_json(tune_path, result)
    logger.info("Wrote ARC tuning metadata: %s (chosen=%s)", tune_path, chosen_params)
    if run_ctx is not None:
        try:
            update_run_metadata(
                run_ctx,
                {
                    "config": {
                        "tune": {
                            "model_name": str(model_name),
                            "search_type": str(search_type),
                            "max_targets": int(max_targets),
                        }
                    },
                    "inputs": {"data_root": str(root)},
                    "artifacts": {"best_config_json_src": str(tune_path)},
                    "metrics": {"tune_scores": tune_scores},
                },
            )
            copy_artifact_into_run(run_ctx, src=tune_path, dest_name="best_config.json")
            finalize_run_success(run_ctx)
        except Exception as e:
            finalize_run_failure(run_ctx, e)
    return tune_path


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
    llm_runtime_attention_mode: str = "auto",
    llm_runtime_disable_compile: bool = False,
    llm_runtime_allocator_expandable_segments: bool = True,
    llm_runtime_allocator_max_split_size_mb: int = 0,
    llm_prefer_cnn_attempt1: bool = False,
    llm_candidate_ranker: str = "default",
) -> Path:
    """Build submission.json using heuristics and/or neural checkpoint (primary model)."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    models_list = [str(m) for m in models] if models else ["baseline_approx"]
    primary = models_list[0]

    stack_raise_if_unsupported_strategy(strategy)

    candidates = [
        root / "arc-agi_test_challenges.json",
        root / "arc-agi_test-challenges.json",
    ]
    test_path = next((p for p in candidates if p.exists()), candidates[0])
    if not test_path.exists():
        raise FileNotFoundError(f"Missing ARC test challenges file: {test_path}")

    test_challenges = read_json(test_path)
    if not isinstance(test_challenges, dict):
        raise ValueError("ARC test challenges JSON must be an object keyed by task id.")

    chosen_params = _resolve_chosen_params_for_submit(
        tuned_config_path,
        train_metadata_json,
        primary,
    )

    entry = _get_per_model_entry(train_metadata_json, primary)
    ckpt_path, cfg_path = _resolve_neural_paths_from_entry(entry)
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
    llm_cfg = _build_llm_tta_config(
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
        llm_runtime_attention_mode=llm_runtime_attention_mode,
        llm_runtime_disable_compile=llm_runtime_disable_compile,
        llm_runtime_allocator_expandable_segments=llm_runtime_allocator_expandable_segments,
        llm_runtime_allocator_max_split_size_mb=llm_runtime_allocator_max_split_size_mb,
        llm_prefer_cnn_attempt1=llm_prefer_cnn_attempt1,
        llm_candidate_ranker=llm_candidate_ranker,
    )
    strategy_telemetry: dict[str, int] = {}

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
            use_strategy_path = str(strategy or "").strip().lower() == "llm_tta_dfs" and not bool(llm_cfg.prefer_cnn_attempt1)
            if use_neural and not use_strategy_path:
                a1 = predict_grid_from_checkpoint(input_grid, ckpt_path, cfg_path)
                a2 = _second_attempt_grid(
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
    write_json(out_path, submission)
    logger.info("Wrote ARC submission (%s strategy, primary_model=%s, neural=%s): %s", strategy, primary, use_neural, out_path)
    if run_ctx is not None:
        try:
            update_run_metadata(
                run_ctx,
                {
                    "config": {
                        "submit": {
                            "strategy": str(strategy),
                            "max_targets": int(max_targets),
                            "models": models_list,
                            "primary_model": primary,
                            "neural_infer": use_neural,
                            "llm_tta_config": {
                                "num_augmentations": int(llm_cfg.num_augmentations),
                                "execution_mode": str(llm_cfg.execution_mode),
                                "beam_width": int(llm_cfg.beam_width),
                                "max_candidates": int(llm_cfg.max_candidates),
                                "max_neg_log_score": float(llm_cfg.max_neg_log_score),
                                "seed": int(llm_cfg.seed),
                                "consistency_weight": float(llm_cfg.consistency_weight),
                                "model_weight": float(llm_cfg.model_weight),
                                "augmentation_likelihood_weight": float(llm_cfg.augmentation_likelihood_weight),
                                "enable_neural_backend": bool(llm_cfg.enable_neural_backend),
                                "model_path": llm_cfg.model_path,
                                "lora_path": llm_cfg.lora_path,
                                "max_runtime_sec": float(llm_cfg.max_runtime_sec),
                                "task_runtime_sec": float(llm_cfg.task_runtime_sec),
                                "decode_runtime_sec": float(llm_cfg.decode_runtime_sec),
                                "adapt_steps": int(llm_cfg.adapt_steps),
                                "adapt_batch_size": int(llm_cfg.adapt_batch_size),
                                "adapt_gradient_accumulation_steps": int(llm_cfg.adapt_gradient_accumulation_steps),
                                "adapt_disabled": bool(llm_cfg.adapt_disabled),
                                "runtime_attention_mode": str(llm_cfg.runtime_attention_mode),
                                "runtime_disable_compile": bool(llm_cfg.runtime_disable_compile),
                                "runtime_allocator_expandable_segments": bool(
                                    llm_cfg.runtime_allocator_expandable_segments
                                ),
                                "runtime_allocator_max_split_size_mb": int(
                                    llm_cfg.runtime_allocator_max_split_size_mb
                                ),
                                "prefer_cnn_attempt1": bool(llm_cfg.prefer_cnn_attempt1),
                                "candidate_ranker": str(llm_cfg.candidate_ranker),
                            },
                            "strategy_telemetry": dict(strategy_telemetry),
                            "tuned_config_path": str(tuned_config_path) if tuned_config_path else None,
                            "train_metadata_json": str(train_metadata_json) if train_metadata_json else None,
                        }
                    },
                    "inputs": {"data_root": str(root)},
                    "artifacts": {"submission_json_src": str(out_path)},
                },
            )
            copy_artifact_into_run(run_ctx, src=out_path, dest_name="submission.json")
            finalize_run_success(run_ctx)
        except Exception as e:
            finalize_run_failure(run_ctx, e)
    return out_path
