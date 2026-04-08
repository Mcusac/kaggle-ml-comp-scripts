"""Schemas for future stacking / OOF artifacts (dataclasses only)."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StackOofPredictionRecord:
    """One row of out-of-fold predictions for a single test cell/task."""

    task_id: str
    test_index: int
    attempt_1: list[list[int]]
    attempt_2: list[list[int]]
    fold_id: int = 0
    meta: dict[str, Any] = field(default_factory=dict)
