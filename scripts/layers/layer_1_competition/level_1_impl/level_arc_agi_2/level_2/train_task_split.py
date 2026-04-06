"""Per-test task views for ARC challenges JSON."""

# FLAG: naming — optional rename to task_test_split (or similar); deferred to reduce import churn.

from __future__ import annotations

import copy
from typing import Any, Mapping


def train_split_task_to_single_test(task: Mapping[str, Any], test_index: int) -> dict[str, Any]:
    """Return a shallow-copied task with ``test`` containing only ``test[test_index]``."""
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    tests = task.get("test")
    if not isinstance(tests, list) or not tests:
        raise ValueError("task has no test list")
    if test_index < 0 or test_index >= len(tests):
        raise IndexError(f"test_index {test_index} out of range for {len(tests)} tests")
    out = {k: copy.deepcopy(v) for k, v in task.items()}
    out["test"] = [copy.deepcopy(tests[test_index])]
    return out


def train_iter_single_test_payloads(task: Mapping[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    """Enumerate ``(idx, single_test_task_dict)`` for each test pair."""
    tests = task.get("test")
    if not isinstance(tests, list):
        return []
    result: list[tuple[int, dict[str, Any]]] = []
    for i in range(len(tests)):
        result.append((i, train_split_task_to_single_test(task, i)))
    return result
