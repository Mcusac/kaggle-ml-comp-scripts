"""Per-grid scoring primitives (cell match + exact match + per-task parsing)."""

from typing import Any


def eval_solution_grids_for_task(
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


def cell_match_counts(
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
