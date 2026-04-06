"""ARC scoring utilities for heuristics and neural checkpoints.

Scores and ranks heuristics by corpus-level scores so the tuning phase
can select strong candidates before submission.

Intra-package dependencies (fully qualified per architecture rules):
  layers...level_arc_agi_2.level_1.heuristics  — predict_attempts_for_heuristic
  layers...level_arc_agi_2.level_1.submit_limits — read_submit_max_tasks_env
"""

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import read_json

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    DEFAULT_SUBMIT_HEURISTIC,
    HEURISTIC_QUICK_ORDER,
    HEURISTIC_THOROUGH_ORDER,
    predict_attempts_for_heuristic,
    read_submit_max_tasks_env,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Private file-system helpers
# ---------------------------------------------------------------------------

def _find_existing(root: Path, names: list[str]) -> Path:
    """Return the first name in ``names`` that exists under ``root``, else ``root/names[0]``."""
    for name in names:
        p = root / name
        if p.is_file():
            return p
    return root / names[0]


def _load_json_path(path: Path) -> Any:
    return read_json(path)


def _eval_solution_grids_for_task(
    solutions_obj: Any,
    task_id: str,
    n_tests: int,
) -> list[list[list[int]] | None]:
    """Best-effort parse of evaluation solutions for one task (ARC layouts vary slightly)."""
    key = task_id if task_id in solutions_obj else str(task_id)
    if key not in solutions_obj:
        return [None] * n_tests
    v = solutions_obj[key]
    grids: list[list[list[int]] | None] = []
    if isinstance(v, list) and v:
        if isinstance(v[0], list):
            if v and isinstance(v[0][0], list):
                for g in v:
                    if isinstance(g, list) and g and isinstance(g[0], list):
                        grids.append(g)  # type: ignore[arg-type]
                    else:
                        grids.append(None)
                while len(grids) < n_tests:
                    grids.append(None)
                return grids[:n_tests]
            return [v[:]] + [None] * (n_tests - 1) if n_tests > 1 else [v[:]]  # type: ignore[list-item]
    return [None] * n_tests


def _cell_match_counts(
    pred: list[list[int]],
    truth: list[list[int]],
) -> tuple[int, int]:
    """Return (total_cells_compared, correct_cells)."""
    if pred == truth:
        t = sum(len(r) for r in truth)
        return t, t
    total = correct = 0
    for pr, tr in zip(pred, truth):
        for pc, tc in zip(pr, tr):
            total += 1
            if pc == tc:
                correct += 1
    return total, correct


def score_grid_exact_match(pred: list[list[int]], truth: list[list[int]]) -> bool:
    """Return True only when both grids match exactly."""
    return pred == truth


# ---------------------------------------------------------------------------
# Public scoring API
# ---------------------------------------------------------------------------

def score_heuristic_on_training_challenges(
    data_root: str,
    heuristic: str,
    *,
    max_tasks: int = 0,
    max_pairs_per_task: int = 0,
) -> float:
    """Mean per-cell accuracy on the training corpus (attempt_1 vs output).

    Iterates each task's ``train`` pairs; no evaluation solutions required.
    """
    root = Path(data_root)
    train_ch_path = _find_existing(
        root,
        [
            "arc-agi_training_challenges.json",
            "arc-agi_training-challenges.json",
        ],
    )
    if not train_ch_path.is_file():
        return 0.0
    challenges = _load_json_path(train_ch_path)
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
            t, c = _cell_match_counts(a1, truth)
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
    train_ch_path = _find_existing(
        root,
        [
            "arc-agi_training_challenges.json",
            "arc-agi_training-challenges.json",
        ],
    )
    if not train_ch_path.is_file():
        return 0.0
    challenges = _load_json_path(train_ch_path)
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
    """Mean per-cell accuracy vs evaluation solutions (attempt_1 only).

    Returns 0.0 when evaluation solutions are not present on disk.
    """
    root = Path(data_root)
    eval_ch_path = _find_existing(
        root,
        [
            "arc-agi_evaluation_challenges.json",
            "arc-agi_evaluation-challenges.json",
        ],
    )
    eval_sol_path = _find_existing(
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
    challenges = _load_json_path(eval_ch_path)
    solutions_raw = _load_json_path(eval_sol_path)
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
        truth_series = _eval_solution_grids_for_task(solutions_raw, str(task_id), bounds)
        for idx in range(bounds):
            pair = tests[idx]
            inp = pair["input"]
            truth = truth_series[idx] if idx < len(truth_series) else None
            if truth is None:
                continue
            a1, _ = predict_attempts_for_heuristic(inp, heuristic)
            t, c = _cell_match_counts(a1, truth)
            total_cells += t
            correct_cells += c
    if total_cells == 0:
        return 0.0
    return correct_cells / float(total_cells)


def rank_heuristics_on_training(
    data_root: str,
    heuristic_order: tuple[str, ...],
    *,
    max_tasks: int = 0,
    max_pairs_per_task: int = 0,
) -> list[tuple[str, float]]:
    """Score each heuristic on training data; return (name, score) sorted descending."""
    ranked: list[tuple[str, float]] = []
    for h in heuristic_order:
        s = score_heuristic_on_training_challenges(
            data_root,
            h,
            max_tasks=max_tasks,
            max_pairs_per_task=max_pairs_per_task,
        )
        ranked.append((h, s))
    ranked.sort(key=lambda x: (-x[1], x[0]))
    return ranked


def select_best_heuristic_on_training(
    data_root: str,
    train_mode: str,
    *,
    max_targets: int = 0,
) -> tuple[dict[str, Any], dict[str, float]]:
    """Pick heuristic using training-challenge ``train`` pairs only.

    No evaluation solutions are required. Returns (chosen_params, scores).
    """
    mode = str(train_mode or "").strip().lower()
    order = HEURISTIC_QUICK_ORDER if mode == "quick" else HEURISTIC_THOROUGH_ORDER
    max_tasks_env = read_submit_max_tasks_env()
    scores: dict[str, float] = {}
    best_h: str | None = None
    best_s = -1.0
    for h in order:
        s = score_heuristic_on_training_challenges(
            data_root,
            h,
            max_tasks=max_tasks_env or 0,
            max_pairs_per_task=int(max_targets or 0),
        )
        scores[h] = s
        if s > best_s:
            best_s = s
            best_h = h
    chosen = best_h or DEFAULT_SUBMIT_HEURISTIC
    return {"heuristic": chosen, "version": 1}, scores


def select_best_heuristic(
    data_root: str,
    search_type: str,
    *,
    max_targets: int = 0,
) -> tuple[dict[str, Any], dict[str, float]]:
    """Pick chosen_params heuristic by evaluation score; ties favour earlier in order."""
    order = HEURISTIC_QUICK_ORDER if search_type == "quick" else HEURISTIC_THOROUGH_ORDER
    max_tasks_env = read_submit_max_tasks_env()
    scores: dict[str, float] = {}
    best_h: str | None = None
    best_s = -1.0
    for h in order:
        s = score_heuristic_on_evaluation(
            data_root,
            h,
            max_tasks=max_tasks_env or 0,
            max_targets=max_targets,
        )
        scores[h] = s
        if s > best_s:
            best_s = s
            best_h = h
    chosen = best_h or DEFAULT_SUBMIT_HEURISTIC
    return {"heuristic": chosen, "version": 1}, scores