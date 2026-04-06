"""Parse ARC solutions JSON entries into per-test grids."""

from __future__ import annotations

from typing import Any


def eval_parse_task_solution_grids(
    solutions_obj: Any,
    task_id: str,
    n_tests: int,
) -> list[list[list[int]] | None]:
    """Best-effort parse of evaluation solutions for one task (same tolerance as train scoring)."""
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


def eval_build_basekey_truth_map(
    challenges: dict[str, Any],
    solutions_raw: dict[str, Any],
    *,
    max_targets: int = 0,
) -> dict[str, list[list[int]]]:
    """Map ``f'{task_id}_{test_index}'`` -> truth grid for labeled tests."""
    labels: dict[str, list[list[int]]] = {}
    for task_id, task in challenges.items():
        if not isinstance(task, dict):
            continue
        tests = task.get("test", [])
        if not isinstance(tests, list) or not tests:
            continue
        bounds = len(tests) if max_targets <= 0 else min(len(tests), int(max_targets))
        truths = eval_parse_task_solution_grids(solutions_raw, str(task_id), bounds)
        for i in range(bounds):
            t = truths[i] if i < len(truths) else None
            if t is None:
                continue
            bk = f"{task_id}_{i}"
            labels[bk] = t
    return labels
