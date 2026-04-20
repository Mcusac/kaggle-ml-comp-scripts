"""ARC grid shape / cell-range validation."""

from typing import Any


def is_valid_grid(grid: Any) -> bool:
    if not isinstance(grid, list) or not grid:
        return False
    if not all(isinstance(row, list) and row for row in grid):
        return False
    width = len(grid[0])
    if width < 1 or width > 30:
        return False
    if len(grid) > 30:
        return False
    for row in grid:
        if len(row) != width:
            return False
        for cell in row:
            if not isinstance(cell, int) or cell < 0 or cell > 9:
                return False
    return True
