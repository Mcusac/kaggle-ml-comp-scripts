"""Contest registry: registration and lookup."""

from .contest_registry import (
    ContestRegistry,
    detect_contest,
    get_contest,
    register_contest,
)

__all__ = [
    "ContestRegistry",
    "detect_contest",
    "get_contest",
    "register_contest",
]
