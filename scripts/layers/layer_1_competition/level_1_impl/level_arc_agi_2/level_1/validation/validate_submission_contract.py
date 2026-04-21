"""ARC sample-submission JSON contract validation (attempt_1/attempt_2 per test)."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.validation.validate_grid_shape import (
    is_valid_grid,
)


def validate_submission_contract(challenges: dict[str, Any], submission: Any) -> None:
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
            if not is_valid_grid(item["attempt_1"]) or not is_valid_grid(item["attempt_2"]):
                raise ValueError(f"Submission[{task_id!r}] contains invalid attempt grid.")
