"""Local-eval pipeline: score a submission JSON against public evaluation solutions."""

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_4 import load_json_raw

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    arc_find_first_existing_file,
    eval_parse_task_solution_grids,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    eval_score_submission_two_attempts,
)


def pipeline_run_score_submission(
    *,
    data_root: str,
    submission_path: str,
    split: str = "evaluation",
) -> dict[str, Any]:
    """Load challenges + solutions + submission JSON; return score and paths used."""
    root = Path(data_root)
    if split.strip().lower() == "evaluation":
        ch_names = ["arc-agi_evaluation_challenges.json", "arc-agi_evaluation-challenges.json"]
        sol_names = ["arc-agi_evaluation_solutions.json", "arc-agi_evaluation-solutions.json"]
    else:
        raise ValueError("Only split='evaluation' is supported for local scoring (needs public solutions).")
    ch_path = arc_find_first_existing_file(root, ch_names)
    sol_path = arc_find_first_existing_file(root, sol_names)
    if ch_path is None or sol_path is None:
        raise FileNotFoundError("Missing evaluation challenges or solutions under data_root.")
    sub_path = Path(submission_path)
    if not sub_path.is_file():
        raise FileNotFoundError(f"Missing submission file: {sub_path}")
    challenges = load_json_raw(ch_path)
    solutions_raw = load_json_raw(sol_path)
    submission = load_json_raw(sub_path)
    if not isinstance(challenges, dict) or not isinstance(solutions_raw, dict) or not isinstance(submission, dict):
        raise ValueError("Invalid JSON structure for challenges, solutions, or submission.")
    replies: dict[str, list[Any]] = {}
    for task_id, task in challenges.items():
        tests = task.get("test", [])
        if not isinstance(tests, list):
            continue
        n = len(tests)
        grids = eval_parse_task_solution_grids(solutions_raw, str(task_id), n)
        replies[str(task_id)] = [g if g is not None else [] for g in grids]
    score = eval_score_submission_two_attempts(replies, submission)
    return {
        "score": score,
        "challenges_path": str(ch_path),
        "solutions_path": str(sol_path),
        "submission_path": str(sub_path),
    }
