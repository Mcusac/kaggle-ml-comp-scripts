"""Shared grid hashable-key helpers.

Two flavors are intentionally distinct:

- :func:`grid_int_hash_key` — integer-normalized (cells coerced with ``int(...)``).
  Used for duplicate detection across ARC candidate grids where colors are always
  integers ``0..9``.
- :func:`reference_hashable_solution` lives in :mod:`.ensemble_reference_rankers`
  and has different semantics (no int cast, only ``tolist()`` when applicable)
  to preserve notebook collision behavior. Keep them separate.
"""

from typing import Any


def grid_int_hash_key(grid: Any) -> tuple[tuple[int, ...], ...]:
    """Integer-normalized hashable key for an ARC grid.

    Coerces cells to ``int`` (0..9 expected) and returns a tuple-of-tuples.
    Accepts ndarrays via ``tolist()``.
    """
    if hasattr(grid, "tolist"):
        grid = grid.tolist()
    return tuple(tuple(int(x) for x in row) for row in grid)
