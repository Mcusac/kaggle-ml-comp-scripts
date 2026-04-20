"""Neural checkpoint scoring vs evaluation solutions (composition tier: imports level_2 inference)."""

from pathlib import Path

from layers.layer_0_core.level_4 import load_json_raw

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import arc_find_first_existing_file
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    eval_solution_grids_for_task,
    score_grid_exact_match,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import predict_grid_from_checkpoint


def score_neural_on_evaluation(
    data_root: str,
    checkpoint_path: str,
    train_config_path: str,
    *,
    max_tasks: int = 0,
    max_targets: int = 0,
) -> float:
    """Exact-match fraction of neural attempt_1 on evaluation solutions."""
    root = Path(data_root)
    eval_ch_path = arc_find_first_existing_file(
        root,
        [
            "arc-agi_evaluation_challenges.json",
            "arc-agi_evaluation-challenges.json",
        ],
    )
    eval_sol_path = arc_find_first_existing_file(
        root,
        [
            "arc-agi_evaluation_solutions.json",
            "arc-agi_evaluation-solutions.json",
        ],
    )
    if eval_ch_path is None or eval_sol_path is None:
        return 0.0

    challenges = load_json_raw(eval_ch_path)
    solutions_raw = load_json_raw(eval_sol_path)
    if not isinstance(challenges, dict) or not isinstance(solutions_raw, dict):
        return 0.0

    task_ids = list(challenges.keys())
    if max_tasks and int(max_tasks) > 0:
        task_ids = task_ids[: int(max_tasks)]

    total_targets = 0
    exact_matches = 0
    for task_id in task_ids:
        task = challenges[task_id]
        tests = task.get("test", [])
        if not isinstance(tests, list) or not tests:
            continue
        bounds = len(tests) if max_targets <= 0 else min(len(tests), int(max_targets))
        truth_series = eval_solution_grids_for_task(solutions_raw, str(task_id), bounds)
        for idx in range(bounds):
            pair = tests[idx]
            inp = pair.get("input")
            truth = truth_series[idx] if idx < len(truth_series) else None
            if not isinstance(inp, list) or truth is None:
                continue
            pred = predict_grid_from_checkpoint(inp, checkpoint_path, train_config_path)
            total_targets += 1
            if score_grid_exact_match(pred, truth):
                exact_matches += 1
    if total_targets == 0:
        return 0.0
    return exact_matches / float(total_targets)
