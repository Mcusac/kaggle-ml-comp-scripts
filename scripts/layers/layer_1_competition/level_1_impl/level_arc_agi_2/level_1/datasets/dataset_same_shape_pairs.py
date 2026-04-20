"""Collect ARC training pairs whose input and output grids share a shape (v0)."""

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json_raw

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    TRAINING_CHALLENGE_NAMES,
    arc_find_first_existing_file,
)

logger = get_logger(__name__)


def _find_training_challenges_json(root: Path) -> Path:
    found = arc_find_first_existing_file(root, list(TRAINING_CHALLENGE_NAMES))
    return found if found is not None else root / TRAINING_CHALLENGE_NAMES[0]


def collect_same_shape_train_pairs(data_root: str) -> list[tuple[list[list[int]], list[list[int]]]]:
    """Pairs where input and output grids share height and width (required for per-cell CE v0)."""
    root = Path(data_root)
    path = _find_training_challenges_json(root)
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
