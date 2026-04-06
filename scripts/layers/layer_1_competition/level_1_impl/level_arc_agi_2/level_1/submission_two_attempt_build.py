"""Build ARC-AGI two-attempt submission dicts (reference ``get_submission`` / ``fill_submission``)."""

from __future__ import annotations

from typing import Any, Mapping

Grid = list[list[int]]


def submission_empty_shell_for_challenges(challenges: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """``task_id -> [ {attempt_1, attempt_2}, ... ]`` with single-cell placeholders per test index."""
    submission: dict[str, list[dict[str, Any]]] = {}
    for task_id, task in challenges.items():
        tid = str(task_id)
        tests = task.get("test") if isinstance(task, dict) else None
        n = len(tests) if isinstance(tests, list) else 0
        submission[tid] = [{"attempt_1": [[0]], "attempt_2": [[0]]} for _ in range(n)]
    return submission


def submission_fill_test_attempts(
    submission: dict[str, list[dict[str, Any]]],
    *,
    task_id: str,
    test_index: int,
    attempt_grids: list[Grid],
) -> None:
    """Write up to two grids into ``submission[task_id][test_index]`` keys ``attempt_1``/``attempt_2``."""
    tid = str(task_id)
    if tid not in submission:
        return
    row = submission[tid]
    if test_index < 0 or test_index >= len(row):
        return
    target = row[test_index]
    for i, g in enumerate(attempt_grids[:2]):
        key = "attempt_1" if i == 0 else "attempt_2"
        if isinstance(g, list) and g:
            target[key] = [[int(c) for c in r] for r in g]
