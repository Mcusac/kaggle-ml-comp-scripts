"""Training pairs and tensor encoding for grid CNN (v0: same-shape input/output only)."""

from pathlib import Path
from typing import Any
from torch.utils.data import Dataset

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_4 import load_json_raw

torch = get_torch()
logger = get_logger(__name__)

CANVAS_SIZE = 32
NUM_CHANNELS = 10


def _find_training_json(root: Path) -> Path:
    for name in ("arc-agi_training_challenges.json", "arc-agi_training-challenges.json"):
        p = root / name
        if p.is_file():
            return p
    return root / "arc-agi_training_challenges.json"


def collect_same_shape_train_pairs(data_root: str) -> list[tuple[list[list[int]], list[list[int]]]]:
    """Pairs where input and output grids share height and width (required for per-cell CE v0)."""
    root = Path(data_root)
    path = _find_training_json(root)
    if not path.is_file():
        return []
    challenges = load_json_raw(path)
    if not isinstance(challenges, dict):
        return []
    pairs: list[tuple[list[list[int]], list[list[int]]]] = []
    for _task_id, task in challenges.items():
        if not isinstance(task, dict):
            continue
        train_pairs = task.get("train", [])
        if not isinstance(train_pairs, list):
            continue
        for pair in train_pairs:
            if not isinstance(pair, dict):
                continue
            inp = pair.get("input")
            out = pair.get("output")
            if not isinstance(inp, list) or not isinstance(out, list):
                continue
            if not inp or not out:
                continue
            if len(inp) != len(out):
                continue
            w_in = len(inp[0]) if inp else 0
            w_out = len(out[0]) if out else 0
            if w_in != w_out:
                continue
            if any(len(row) != w_in for row in inp) or any(len(row) != w_out for row in out):
                continue
            pairs.append((inp, out))
    logger.info("Collected %d same-shape train pairs for neural v0", len(pairs))
    return pairs


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
) -> torch.Tensor:
    """Float tensor shape ``(NUM_CHANNELS, canvas, canvas)``."""
    padded = pad_grid_to_canvas(grid, canvas=canvas)
    t = torch.zeros(NUM_CHANNELS, canvas, canvas, dtype=torch.float32)
    for i, row in enumerate(padded):
        for j, v in enumerate(row):
            if 0 <= int(v) < NUM_CHANNELS:
                t[int(v), i, j] = 1.0
    return t


def logits_to_grid(
    logits: torch.Tensor,
    orig_h: int,
    orig_w: int,
) -> list[list[int]]:
    """Argmax spatial logits ``(num_classes,H,W)`` trimmed to original size (v0 limitation)."""
    pred = logits.argmax(dim=0)
    h = min(orig_h, pred.shape[0])
    w = min(orig_w, pred.shape[1])
    return [[int(pred[i, j].item()) for j in range(w)] for i in range(h)]


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
