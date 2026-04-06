"""Rectangular grid equality (numeric cells), tolerating numpy-backed rows."""

from __future__ import annotations

from typing import Any


def arc_grids_equal(a: Any, b: Any) -> bool:
    """Return True if ``a`` and ``b`` are row-major ARC-style int grids of the same shape."""
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
