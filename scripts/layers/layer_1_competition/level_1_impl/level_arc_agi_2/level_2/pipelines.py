"""Starter ARC pipelines for train, tune, and submit."""

import json

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import ARC26Paths, ARC26PostProcessor
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    update_run_metadata,
)

logger = get_logger(__name__)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(data: Any, path: Path) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _build_blank_grid_like(input_grid: list[list[int]]) -> list[list[int]]:
    return [[0 for _ in row] for row in input_grid]


def run_train_pipeline(
    data_root: str,
    train_mode: str,
    models: list[str],
    run_ctx: Optional[RunContext] = None,
) -> Path:
    """Persist deterministic starter metadata for train stage."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    out_dir = ARC26Paths().get_output_dir() / "models" / "arc_agi_2"
    ensure_dir(out_dir)
    metadata_path = out_dir / "train_metadata.json"
    metadata = {
        "contest": "arc_agi_2",
        "train_mode": str(train_mode),
        "models": [str(m) for m in models],
        "data_root": str(root),
        "status": "starter_complete",
    }
    _save_json(metadata, metadata_path)
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
    """Persist deterministic starter tuning artifact."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    out_dir = ARC26Paths().get_output_dir() / "models" / "arc_agi_2" / str(model_name)
    ensure_dir(out_dir)
    tune_path = out_dir / "best_config.json"
    result = {
        "model_name": str(model_name),
        "search_type": str(search_type),
        "max_targets": int(max_targets),
        "chosen_params": {"heuristic": "blank_grid", "version": 1},
    }
    _save_json(result, tune_path)
    logger.info("Wrote ARC tuning metadata: %s", tune_path)
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
) -> Path:
    """Create a valid ARC submission.json baseline."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    candidates = [
        root / "arc-agi_test_challenges.json",
        root / "arc-agi_test-challenges.json",
    ]
    test_path = next((p for p in candidates if p.exists()), candidates[0])
    if not test_path.exists():
        raise FileNotFoundError(f"Missing ARC test challenges file: {test_path}")

    test_challenges = _load_json(test_path)
    if not isinstance(test_challenges, dict):
        raise ValueError("ARC test challenges JSON must be an object keyed by task id.")

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
            blank = _build_blank_grid_like(input_grid)
            entries.append({"attempt_1": blank, "attempt_2": blank})
        submission[str(task_id)] = entries

    submission = ARC26PostProcessor().normalize_submission(submission)
    out_path = Path(output_json) if output_json else ARC26Paths().submission_output_path()
    _save_json(submission, out_path)
    logger.info("Wrote ARC submission (%s strategy): %s", strategy, out_path)
    if run_ctx is not None:
        try:
            update_run_metadata(
                run_ctx,
                {
                    "config": {"submit": {"strategy": str(strategy), "max_targets": int(max_targets)}},
                    "inputs": {"data_root": str(root)},
                    "artifacts": {"submission_json_src": str(out_path)},
                },
            )
            copy_artifact_into_run(run_ctx, src=out_path, dest_name="submission.json")
            finalize_run_success(run_ctx)
        except Exception as e:
            finalize_run_failure(run_ctx, e)
    return out_path

