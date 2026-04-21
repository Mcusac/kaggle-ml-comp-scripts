"""Pure integer-grid helpers shared across competition workflows."""

from typing import Any


def arc_grids_equal(a: Any, b: Any) -> bool:
    """Return True if ``a`` and ``b`` are row-major int grids of the same shape."""
    if a is None or b is None:
        return False
    if hasattr(a, "tolist"):
        a = a.tolist()
    if hasattr(b, "tolist"):
        b = b.tolist()
    if not isinstance(a, list) or not isinstance(b, list):
        return False
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if not isinstance(ra, list) or not isinstance(rb, list) or len(ra) != len(rb):
            return False
        if any(int(x) != int(y) for x, y in zip(ra, rb)):
            return False
    return True


def grid_int_hash_key(grid: Any) -> tuple[tuple[int, ...], ...]:
    """Integer-normalized hashable key for a 2D grid (cells coerced with ``int``)."""
    if hasattr(grid, "tolist"):
        grid = grid.tolist()
    return tuple(tuple(int(x) for x in row) for row in grid)


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


__all__ = [
    "arc_grids_equal",
    "cell_match_counts",
    "grid_int_hash_key",
    "score_grid_exact_match",
]
