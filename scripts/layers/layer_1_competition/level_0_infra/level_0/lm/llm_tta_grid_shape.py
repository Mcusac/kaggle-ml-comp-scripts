"""Shape-only grid helpers for LLM-TTA (no palette / coercion semantics)."""

Grid = list[list[int]]


def llm_tta_grid_hw(grid: Grid) -> tuple[int, int]:
    """Return ``(rows, cols)`` for ``grid``; ``(0, 0)`` when empty."""
    if not grid:
        return 0, 0
    return len(grid), len(grid[0])


def empty_grid_like(grid: Grid) -> Grid:
    """Zero-filled grid with the same shape as ``grid``."""
    return [[0 for _ in row] for row in grid]


def llm_tta_augment_seed(task_id: str, test_index: int, base_seed: int) -> int:
    """Deterministic per-task augmentation seed derived from ``task_id`` and ``test_index``."""
    return int(base_seed) + sum(ord(ch) for ch in str(task_id)) + int(test_index) * 9973