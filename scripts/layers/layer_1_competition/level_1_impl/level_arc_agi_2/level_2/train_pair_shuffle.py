"""Deterministic shuffle of ARC ``train`` demonstration pairs."""

# FLAG: naming — optional rename to task_train_shuffle (or similar); deferred to reduce import churn.

from __future__ import annotations

import copy
import random
from typing import Any, Mapping


def train_shuffle_train_pairs(task: Mapping[str, Any], *, seed: int) -> dict[str, Any]:
    """Return a deep copy of ``task`` with ``train`` list order permuted."""
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    train = task.get("train")
    if not isinstance(train, list) or not train:
        return {k: copy.deepcopy(v) for k, v in task.items()}
    rng = random.Random(int(seed))
    idx = list(range(len(train)))
    rng.shuffle(idx)
    permuted = [copy.deepcopy(train[j]) for j in idx]
    out = {k: copy.deepcopy(v) for k, v in task.items()}
    out["train"] = permuted
    return out
