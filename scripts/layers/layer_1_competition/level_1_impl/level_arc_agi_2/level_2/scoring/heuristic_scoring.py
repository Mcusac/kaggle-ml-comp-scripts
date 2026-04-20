"""Corpus-level heuristic scoring on training and evaluation challenges."""

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json_raw

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    arc_find_first_existing_file,
    predict_attempts_for_heuristic,
    cell_match_counts,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    eval_solution_grids_for_task,
    score_grid_exact_match,
)

logger = get_logger(__name__)


def _first_existing_or_default(root: Path, names: list[str]) -> Path:
    """Return the first file from ``names`` that exists under ``root``, else ``root/names[0]``."""
    found = arc_find_first_existing_file(root, names)
    return found if found is not None else (root / names[0])


def score_heuristic_on_training_challenges(
    data_root: str,
    heuristic: str,
    *,
    max_tasks: int = 0,
    max_pairs_per_task: int = 0,
) -> float:
    """Mean per-cell accuracy on the training corpus (attempt_1 vs output)."""
    root = Path(data_root)
    train_ch_path = _first_existing_or_default(
        root,
        [
            "arc-agi_training_challenges.json",
            "arc-agi_training-challenges.json",
        ],
    )
    if not train_ch_path.is_file():
        return 0.0
    challenges = load_json_raw(train_ch_path)
    if not isinstance(challenges, dict):
        return 0.0

    task_ids = list(challenges.keys())
    if max_tasks and int(max_tasks) > 0:
        task_ids = task_ids[: int(max_tasks)]

    total_cells = 0
    correct_cells = 0
    for task_id in task_ids:
        task = challenges[task_id]
        train_pairs = task.get("train", [])
        if not isinstance(train_pairs, list) or not train_pairs:
            continue
        bounds = (
            len(train_pairs)
            if max_pairs_per_task <= 0
            else min(len(train_pairs), int(max_pairs_per_task))
        )
        for idx in range(bounds):
            pair = train_pairs[idx]
            inp = pair.get("input")
            truth = pair.get("output")
            if not isinstance(inp, list) or not isinstance(truth, list):
                continue
            a1, _ = predict_attempts_for_heuristic(inp, heuristic)
            t, c = cell_match_counts(a1, truth)
            total_cells += t
            correct_cells += c
    if total_cells == 0:
        return 0.0
    return correct_cells / float(total_cells)


def score_heuristic_exact_match_on_training(
    data_root: str,
    heuristic: str,
    *,
    max_tasks: int = 0,
    max_pairs_per_task: int = 0,
) -> float:
    """Fraction of training pairs where attempt_1 is an exact grid match."""
    root = Path(data_root)
    train_ch_path = _first_existing_or_default(
        root,
        [
            "arc-agi_training_challenges.json",
            "arc-agi_training-challenges.json",
        ],
    )
    if not train_ch_path.is_file():
        return 0.0
    challenges = load_json_raw(train_ch_path)
    if not isinstance(challenges, dict):
        return 0.0

    task_ids = list(challenges.keys())
    if max_tasks and int(max_tasks) > 0:
        task_ids = task_ids[: int(max_tasks)]

    total_pairs = 0
    exact_matches = 0
    for task_id in task_ids:
        task = challenges[task_id]
        train_pairs = task.get("train", [])
        if not isinstance(train_pairs, list) or not train_pairs:
            continue
        bounds = (
            len(train_pairs)
            if max_pairs_per_task <= 0
            else min(len(train_pairs), int(max_pairs_per_task))
        )
        for idx in range(bounds):
            pair = train_pairs[idx]
            inp = pair.get("input")
            truth = pair.get("output")
            if not isinstance(inp, list) or not isinstance(truth, list):
                continue
            a1, _ = predict_attempts_for_heuristic(inp, heuristic)
            total_pairs += 1
            if score_grid_exact_match(a1, truth):
                exact_matches += 1
    if total_pairs == 0:
        return 0.0
    return exact_matches / float(total_pairs)


def score_heuristic_on_evaluation(
    data_root: str,
    heuristic: str,
    *,
    max_tasks: int = 0,
    max_targets: int = 0,
) -> float:
    """Mean per-cell accuracy vs evaluation solutions (attempt_1 only)."""
    root = Path(data_root)
    eval_ch_path = _first_existing_or_default(
        root,
        [
            "arc-agi_evaluation_challenges.json",
            "arc-agi_evaluation-challenges.json",
        ],
    )
    eval_sol_path = _first_existing_or_default(
        root,
        [
            "arc-agi_evaluation_solutions.json",
            "arc-agi_evaluation-solutions.json",
        ],
    )
    if not eval_ch_path.is_file():
        return 0.0
    if not eval_sol_path.is_file():
        logger.info("No evaluation solutions on disk; skipping tune scoring for %s", heuristic)
        return 0.0
    challenges = load_json_raw(eval_ch_path)
    solutions_raw = load_json_raw(eval_sol_path)
    if not isinstance(challenges, dict) or not isinstance(solutions_raw, dict):
        return 0.0

    task_ids = list(challenges.keys())
    if max_tasks and int(max_tasks) > 0:
        task_ids = task_ids[: int(max_tasks)]

    total_cells = 0
    correct_cells = 0
    for task_id in task_ids:
        task = challenges[task_id]
        tests = task.get("test", [])
        if not isinstance(tests, list) or not tests:
            continue
        bounds = len(tests) if max_targets <= 0 else min(len(tests), int(max_targets))
        truth_series = eval_solution_grids_for_task(solutions_raw, str(task_id), bounds)
        for idx in range(bounds):
            pair = tests[idx]
            inp = pair["input"]
            truth = truth_series[idx] if idx < len(truth_series) else None
            if truth is None:
                continue
            a1, _ = predict_attempts_for_heuristic(inp, heuristic)
            t, c = cell_match_counts(a1, truth)
            total_cells += t
            correct_cells += c
    if total_cells == 0:
        return 0.0
    return correct_cells / float(total_cells)

