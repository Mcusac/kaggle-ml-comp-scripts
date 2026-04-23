"""Baseline heuristics for ARC attempt generation.

Provides named heuristics that produce two candidate grids (attempt_1, attempt_2)
for a given input grid, plus helpers for selecting among them from stored params.
"""

from copy import deepcopy
from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)

DEFAULT_SUBMIT_HEURISTIC = "copy_input"

HEURISTIC_QUICK_ORDER: tuple[str, ...] = ("copy_input", "blank_grid")
HEURISTIC_THOROUGH_ORDER: tuple[str, ...] = ("copy_input", "blank_grid", "most_common_color")


def _build_blank_grid_like(input_grid: list[list[int]]) -> list[list[int]]:
    return [[0 for _ in row] for row in input_grid]


def _most_common_non_zero_color(input_grid: list[list[int]]) -> int:
    counts: dict[int, int] = {}
    for row in input_grid:
        for value in row:
            color = int(value)
            if color == 0:
                continue
            counts[color] = counts.get(color, 0) + 1
    if not counts:
        return 0
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def heuristic_order_for_train_mode(train_mode: str) -> tuple[str, ...]:
    """Return the ordered heuristic tuple for a given training mode string."""
    m = str(train_mode or "").strip().lower()
    return HEURISTIC_QUICK_ORDER if m == "quick" else HEURISTIC_THOROUGH_ORDER


def predict_attempts_for_heuristic(
    input_grid: list[list[int]],
    heuristic: str,
) -> tuple[list[list[int]], list[list[int]]]:
    """Return (attempt_1, attempt_2) for a named baseline heuristic."""
    h = str(heuristic or "").strip() or DEFAULT_SUBMIT_HEURISTIC
    if h == "blank_grid":
        b = _build_blank_grid_like(input_grid)
        return b, deepcopy(b)
    if h == "most_common_color":
        fill = _most_common_non_zero_color(input_grid)
        out = [[fill for _ in row] for row in input_grid]
        return out, _build_blank_grid_like(input_grid)
    if h == "copy_input":
        a1 = deepcopy(input_grid)
        return a1, _build_blank_grid_like(input_grid)
    _logger.warning("Unknown heuristic %r; falling back to %s", h, DEFAULT_SUBMIT_HEURISTIC)
    return predict_attempts_for_heuristic(input_grid, DEFAULT_SUBMIT_HEURISTIC)


def predict_attempts_from_chosen_params(
    input_grid: list[list[int]],
    chosen_params: Mapping[str, Any] | None,
) -> tuple[list[list[int]], list[list[int]]]:
    """Derive the heuristic from chosen_params and produce two attempts."""
    if not chosen_params:
        return predict_attempts_for_heuristic(input_grid, DEFAULT_SUBMIT_HEURISTIC)
    h = chosen_params.get("heuristic", DEFAULT_SUBMIT_HEURISTIC)
    return predict_attempts_for_heuristic(input_grid, str(h))