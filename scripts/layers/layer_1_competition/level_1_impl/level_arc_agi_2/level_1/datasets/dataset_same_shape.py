"""PyTorch ``Dataset`` wrapper for same-shape ARC pairs (v0)."""

from typing import Any

from torch.utils.data import Dataset

from layers.layer_0_core.level_0 import get_torch

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    CANVAS_SIZE,
    grid_to_one_hot_tensor,
    pad_grid_to_canvas,
)

torch = get_torch()


class ArcSameShapeGridDataset(Dataset):
    """One-hot input and class-target output on a fixed canvas."""

    def __init__(self, pairs: list[tuple[list[list[int]], list[list[int]]]], canvas: int = CANVAS_SIZE):
        self._pairs = pairs
        self._canvas = canvas

    def __len__(self) -> int:
        return len(self._pairs)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any]]:
        inp, out = self._pairs[idx]
        oh = grid_to_one_hot_tensor(inp, canvas=self._canvas)
        padded_out = pad_grid_to_canvas(out, canvas=self._canvas)
        target = torch.tensor(padded_out, dtype=torch.long)
        meta = {"orig_h": len(inp), "orig_w": len(inp[0]) if inp else 0}
        return oh, target, meta
