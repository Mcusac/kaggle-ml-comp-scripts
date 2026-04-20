"""Grid utilities and support-grid probability builders for the LLM-TTA strategy."""

from typing import Any, Mapping

Grid = list[list[int]]


def llm_tta_grid_hw(grid: Grid) -> tuple[int, int]:
    """Return ``(rows, cols)`` for ``grid``; ``(0, 0)`` when empty."""
    if not grid:
        return 0, 0
    return len(grid), len(grid[0])


def empty_arc_grid_like(grid: Grid) -> Grid:
    """Zero-filled grid with the same shape as ``grid``."""
    return [[0 for _ in row] for row in grid]


def coerce_arc_grid(grid: Any, fallback: Grid) -> Grid:
    """Return a clean rectangular ``list[list[int]]`` with values mod 10, or ``fallback`` on failure."""
    if not isinstance(grid, list):
        return fallback
    if not grid:
        return []
    if not all(isinstance(row, list) for row in grid):
        return fallback
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        return fallback
    try:
        return [[int(v) % 10 for v in row] for row in grid]
    except Exception:
        return fallback


def collect_llm_tta_support_grids(
    task_payload: Mapping[str, Any] | None, default_grid: Grid
) -> list[Grid]:
    """Extract output grids from the task's training pairs; fall back to ``[default_grid]``."""
    support: list[Grid] = []
    if not task_payload:
        return [default_grid]
    train = task_payload.get("train")
    if isinstance(train, list):
        for pair in train:
            if not isinstance(pair, dict):
                continue
            out_grid = pair.get("output")
            if isinstance(out_grid, list):
                support.append(coerce_arc_grid(out_grid, default_grid))
    if support:
        return support
    support.append(default_grid)
    return support


def build_cell_probs_from_support_grids(
    grids: list[Grid], h: int, w: int
) -> list[list[list[float]]]:
    """Per-cell 10-way color distribution aggregated over ``grids`` with Laplace smoothing."""
    probs = [[[0.0 for _ in range(10)] for _ in range(w)] for _ in range(h)]
    if not grids or h <= 0 or w <= 0:
        return probs
    for r in range(h):
        for c in range(w):
            counts = [1e-3 for _ in range(10)]
            for grid in grids:
                if r < len(grid) and c < len(grid[r]):
                    color = int(grid[r][c]) % 10
                    counts[color] += 1.0
            total = float(sum(counts))
            probs[r][c] = [float(v / total) for v in counts]
    return probs


def llm_tta_augment_seed(task_id: str, test_index: int, base_seed: int) -> int:
    """Deterministic per-task augmentation seed derived from ``task_id`` and ``test_index``."""
    return int(base_seed) + sum(ord(ch) for ch in str(task_id)) + int(test_index) * 9973
