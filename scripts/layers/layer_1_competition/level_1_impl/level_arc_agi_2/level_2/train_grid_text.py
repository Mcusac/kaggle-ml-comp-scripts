"""Grid to/from newline digit text (reference notebook style).

Delegates to :mod:`arc_digit_grid_text` in level_0 (single source of truth).
"""

from __future__ import annotations

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_digit_grid_text import (
    MAX_ARC_GRID_DIM,
    arc_grid_to_text_lines,
    arc_is_valid_grid_shape,
    arc_text_lines_to_grid,
)

Grid = list[list[int]]
MAX_DIM = MAX_ARC_GRID_DIM

train_grid_to_text_lines = arc_grid_to_text_lines
train_is_valid_arc_grid_shape = arc_is_valid_grid_shape
train_text_lines_to_grid = arc_text_lines_to_grid

__all__ = [
    "Grid",
    "MAX_DIM",
    "train_grid_to_text_lines",
    "train_is_valid_arc_grid_shape",
    "train_text_lines_to_grid",
]
