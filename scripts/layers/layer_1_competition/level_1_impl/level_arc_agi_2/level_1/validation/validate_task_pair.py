"""ARC per-task-pair (train/test) contract validation."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.validation.validate_grid_shape import (
    _is_valid_grid,
)


def _validate_task_pair(pair: Any, include_output: bool = True) -> None:
    if not isinstance(pair, dict):
        raise ValueError("Task pair must be a dict.")
    if "input" not in pair:
        raise ValueError("Task pair missing 'input'.")
    if not _is_valid_grid(pair["input"]):
        raise ValueError("Task pair has invalid input grid.")
    if include_output:
        if "output" not in pair:
            raise ValueError("Task pair missing 'output'.")
        if not _is_valid_grid(pair["output"]):
            raise ValueError("Task pair has invalid output grid.")
