"""Path-returning ARC pipeline stages (train / tune / submit)."""

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger

from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir, read_json, write_json

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ARC26Paths, 
    ARC26PostProcessor,
    DEFAULT_SUBMIT_HEURISTIC,
    load_chosen_params_from_tuned_config,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
    rank_heuristics_on_training,
    read_submit_max_tasks_env,
    select_best_heuristic,
    select_best_heuristic_on_training,
    _heuristic_order_for_train_mode,
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    update_run_metadata,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    predict_grid_from_checkpoint,
    predict_attempts_for_submit_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import get_trainer, list_available_models

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
        order = _heuristic_order_for_train_mode(train_mode)
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
    result = {
        "model_name": str(model_name),
        "search_type": str(search_type),
        "max_targets": int(max_targets),
        "chosen_params": chosen_params,
        "tune_scores": tune_scores,
    }
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
) -> Path:
    """Build submission.json using heuristics and/or neural checkpoint (primary model)."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    models_list = [str(m) for m in models] if models else ["baseline_approx"]
    primary = models_list[0]

    strat = str(strategy or "").strip().lower()
    if strat in ("stacking", "stacking_ensemble"):
        raise ValueError(
            f"Strategy {strategy!r} is not implemented for ARC (requires validation predictions). "
            "Use single or ensemble."
        )

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
            if use_neural:
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
                a1, a2 = predict_attempts_for_submit_strategy(
                    input_grid,
                    strategy=strategy,
                    chosen_params=chosen_params,
                    data_root=str(root),
                    train_mode=str(train_mode),
                    max_pairs_per_task=int(max_targets or 0),
                )
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
