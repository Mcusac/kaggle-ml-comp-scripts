"""Safe file move planning utilities (no I/O)."""

from .move_plan import (
    MovePlan,
    MovePlanError,
    MoveSpec,
    compute_move_plan,
)

__all__ = [
    "MovePlan",
    "MovePlanError",
    "MoveSpec",
    "compute_move_plan",
]

