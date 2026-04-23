"""One-hot / argmax tensor encoding for fixed-canvas ARC grids (v0)."""

from layers.layer_0_core.level_0 import get_torch

_torch = get_torch()

CANVAS_SIZE = 32
NUM_CHANNELS = 10


def pad_grid_to_canvas(grid: list[list[int]], canvas: int = CANVAS_SIZE, fill: int = 0) -> list[list[int]]:
    h, w = len(grid), len(grid[0]) if grid else (0, 0)
    out = [[fill for _ in range(canvas)] for _ in range(canvas)]
    for i in range(min(h, canvas)):
        for j in range(min(w, canvas)):
            out[i][j] = grid[i][j]
    return out


def grid_to_one_hot_tensor(
    grid: list[list[int]],
    canvas: int = CANVAS_SIZE,
) -> _torch.Tensor:
    """Float tensor shape ``(NUM_CHANNELS, canvas, canvas)``."""
    padded = pad_grid_to_canvas(grid, canvas=canvas)
    t = _torch.zeros(NUM_CHANNELS, canvas, canvas, dtype=_torch.float32)
    for i, row in enumerate(padded):
        for j, v in enumerate(row):
            if 0 <= int(v) < NUM_CHANNELS:
                t[int(v), i, j] = 1.0
    return t


def logits_to_grid(
    logits: _torch.Tensor,
    orig_h: int,
    orig_w: int,
) -> list[list[int]]:
    """Argmax spatial logits ``(num_classes,H,W)`` trimmed to original size (v0 limitation)."""
    pred = logits.argmax(dim=0)
    h = min(orig_h, pred.shape[0])
    w = min(orig_w, pred.shape[1])
    return [[int(pred[i, j].item()) for j in range(w)] for i in range(h)]
