"""Contest-supplied callables for :class:`SharedTorchLmInference` (no ARC imports)."""

from dataclasses import dataclass
from typing import Any, Callable

Grid = list[list[int]]


@dataclass(frozen=True)
class SharedTorchLmHooks:
    """Wires chat formatting, turbo DFS, and grid text used by the shared inference mixin."""

    make_formatter: Callable[[Any], Any]
    inference_turbo_dfs: Callable[..., Any]
    arc_grid_to_text_lines: Callable[[Grid], Any]
    reference_inner_loop_wall_sec: float


__all__ = [
    "Grid",
    "SharedTorchLmHooks",
]
