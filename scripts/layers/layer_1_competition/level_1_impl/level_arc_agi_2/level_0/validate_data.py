"""ARC JSON contract validation."""

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json

logger = get_logger(__name__)


def _is_valid_grid(grid: Any) -> bool:
    if not isinstance(grid, list) or not grid:
        return False
    if not all(isinstance(row, list) and row for row in grid):
        return False
    width = len(grid[0])
    if width < 1 or width > 30:
        return False
    if len(grid) > 30:
        return False
    for row in grid:
        if len(row) != width:
            return False
        for cell in row:
            if not isinstance(cell, int) or cell < 0 or cell > 9:
                return False
    return True


def _validate_task_pair(pair: Any, include_output: bool = True) -> None:
    if not isinstance(pair, dict):
        raise ValueError("Task pair must be a dict.")
    if "input" not in pair:
        raise ValueError("Task pair missing 'input'.")
    if not _is_valid_grid(pair["input"]):
        raise ValueError("Task pair has invalid input grid.")
    if include_output:
        if "output" not in pair:
            raise ValueError("Task pair missing 'output'.")
        if not _is_valid_grid(pair["output"]):
            raise ValueError("Task pair has invalid output grid.")


def _validate_challenges(challenges: Any, max_targets: int = 0) -> None:
    if not isinstance(challenges, dict):
        raise ValueError("Challenges JSON must be a dict keyed by task id.")
    for task_id, task in challenges.items():
        if not str(task_id).strip():
            raise ValueError("Encountered empty task id.")
        if not isinstance(task, dict):
            raise ValueError(f"Task {task_id!r} must map to a dict.")
        train_pairs = task.get("train")
        test_pairs = task.get("test")
        if not isinstance(train_pairs, list) or not train_pairs:
            raise ValueError(f"Task {task_id!r} has invalid train pairs.")
        if not isinstance(test_pairs, list) or not test_pairs:
            raise ValueError(f"Task {task_id!r} has invalid test pairs.")
        for pair in train_pairs:
            _validate_task_pair(pair, include_output=True)
        bound = len(test_pairs) if max_targets <= 0 else min(len(test_pairs), int(max_targets))
        for pair in test_pairs[:bound]:
            _validate_task_pair(pair, include_output=False)


def _validate_submission_contract(challenges: dict[str, Any], submission: Any) -> None:
    if not isinstance(submission, dict):
        raise ValueError("Submission JSON must be a dict keyed by task id.")
    challenge_task_ids = set(challenges.keys())
    submission_task_ids = set(submission.keys())
    if challenge_task_ids != submission_task_ids:
        missing = sorted(challenge_task_ids - submission_task_ids)
        extra = sorted(submission_task_ids - challenge_task_ids)
        raise ValueError(
            f"Submission task ids mismatch. Missing={missing[:5]}, extra={extra[:5]}"
        )
    for task_id in sorted(challenge_task_ids):
        task_entries = submission[task_id]
        if not isinstance(task_entries, list):
            raise ValueError(f"Submission[{task_id!r}] must be a list.")
        expected_len = len(challenges[task_id]["test"])
        if len(task_entries) != expected_len:
            raise ValueError(
                f"Submission[{task_id!r}] expected {expected_len} test entries, got {len(task_entries)}."
            )
        for item in task_entries:
            if not isinstance(item, dict):
                raise ValueError(f"Submission[{task_id!r}] entries must be dicts.")
            if "attempt_1" not in item or "attempt_2" not in item:
                raise ValueError(f"Submission[{task_id!r}] entries must include attempt_1 and attempt_2.")
            if not _is_valid_grid(item["attempt_1"]) or not _is_valid_grid(item["attempt_2"]):
                raise ValueError(f"Submission[{task_id!r}] contains invalid attempt grid.")


def validate_arc_inputs(data_root: str, max_targets: int = 0) -> None:
    """Validate ARC challenge files and sample submission contract."""
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    train_challenges = next(
        (
            p for p in [
                root / "arc-agi_training_challenges.json",
                root / "arc-agi_training-challenges.json",
            ] if p.exists()
        ),
        root / "arc-agi_training_challenges.json",
    )
    eval_challenges = next(
        (
            p for p in [
                root / "arc-agi_evaluation_challenges.json",
                root / "arc-agi_evaluation-challenges.json",
            ] if p.exists()
        ),
        root / "arc-agi_evaluation_challenges.json",
    )
    test_challenges = next(
        (
            p for p in [
                root / "arc-agi_test_challenges.json",
                root / "arc-agi_test-challenges.json",
            ] if p.exists()
        ),
        root / "arc-agi_test_challenges.json",
    )
    sample_submission = root / "sample_submission.json"

    for p in [train_challenges, eval_challenges, test_challenges]:
        if not p.exists():
            raise FileNotFoundError(f"Missing required ARC file: {p}")

    train_data = load_json(train_challenges)
    eval_data = load_json(eval_challenges)
    test_data = load_json(test_challenges)

    _validate_challenges(train_data, max_targets=max_targets)
    _validate_challenges(eval_data, max_targets=max_targets)
    _validate_challenges(test_data, max_targets=max_targets)

    if sample_submission.exists():
        sample_data = load_json(sample_submission)
        _validate_submission_contract(test_data, sample_data)

    logger.info("ARC inputs validated")
    logger.info("  train tasks: %d", len(train_data))
    logger.info("  evaluation tasks: %d", len(eval_data))
    logger.info("  test tasks: %d", len(test_data))

