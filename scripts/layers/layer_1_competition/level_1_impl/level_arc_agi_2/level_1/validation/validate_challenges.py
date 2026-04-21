"""ARC challenges JSON contract validation (task-id keyed dict of train/test pairs)."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validation.validate_task_pair import (
    validate_task_pair,
)


def validate_challenges(challenges: Any, max_targets: int = 0) -> None:
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
            validate_task_pair(pair, include_output=True)
        bound = len(test_pairs) if max_targets <= 0 else min(len(test_pairs), int(max_targets))
        for pair in test_pairs[:bound]:
            validate_task_pair(pair, include_output=False)
