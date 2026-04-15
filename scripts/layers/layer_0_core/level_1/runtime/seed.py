"""Reproducibility utilities."""

import os
import random
import numpy as np

from layers.layer_0_core.level_0 import get_torch


def set_seed(seed: int, deterministic: bool = True) -> None:
    """
    Set random seeds for reproducibility.

    Args:
        seed: Random seed value
        deterministic: Whether to enable deterministic torch backend behavior

    Raises:
        ValueError: If seed is not an int or not in [0, 2^32).
    """
    if not isinstance(seed, int):
        raise ValueError(f"seed must be int, got {type(seed).__name__}")
    if not (0 <= seed < 2**32):
        raise ValueError(f"seed must be in range [0, 2^32), got {seed}")

    os.environ["PYTHONHASHSEED"] = str(seed)

    random.seed(seed)
    np.random.seed(seed)

    torch = get_torch()
    if torch is None:
        return

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
