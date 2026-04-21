"""Per-grid scoring: ARC eval JSON parsing plus generic cell/exact-match metrics."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import (
    cell_match_counts as _cell_match_counts,
    score_grid_exact_match as _score_grid_exact_match,
)

cell_match_counts = _cell_match_counts
score_grid_exact_match = _score_grid_exact_match


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
