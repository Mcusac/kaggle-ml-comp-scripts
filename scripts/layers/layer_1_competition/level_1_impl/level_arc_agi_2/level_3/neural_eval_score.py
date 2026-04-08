"""Neural checkpoint scoring vs evaluation solutions (composition tier: imports level_2 inference)."""

from pathlib import Path

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import scoring as _arc_scoring
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
    eval_ch_path = _arc_scoring._find_existing(
        root,
        [
            "arc-agi_evaluation_challenges.json",
            "arc-agi_evaluation-challenges.json",
        ],
    )
    eval_sol_path = _arc_scoring._find_existing(
        root,
        [
            "arc-agi_evaluation_solutions.json",
            "arc-agi_evaluation-solutions.json",
        ],
    )
    if not eval_ch_path.is_file() or not eval_sol_path.is_file():
        return 0.0
    challenges = _arc_scoring._load_json_path(eval_ch_path)
    solutions_raw = _arc_scoring._load_json_path(eval_sol_path)
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
        truth_series = _arc_scoring._eval_solution_grids_for_task(solutions_raw, str(task_id), bounds)
        for idx in range(bounds):
            pair = tests[idx]
            inp = pair.get("input")
            truth = truth_series[idx] if idx < len(truth_series) else None
            if not isinstance(inp, list) or truth is None:
                continue
            pred = predict_grid_from_checkpoint(inp, checkpoint_path, train_config_path)
            total_targets += 1
            if _arc_scoring.score_grid_exact_match(pred, truth):
                exact_matches += 1
    if total_targets == 0:
        return 0.0
    return exact_matches / float(total_targets)
