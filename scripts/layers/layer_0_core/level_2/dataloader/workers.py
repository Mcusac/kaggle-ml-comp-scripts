"""Worker initialisation for deterministic DataLoader behaviour."""

from typing import Callable

from level_1 import set_seed


def create_worker_init_fn(seed: int) -> Callable[[int], None]:
    """
    Return a worker initialisation function that seeds each worker deterministically.

    Each worker receives a unique seed derived from the base seed and its ID,
    ensuring reproducible but independent data loading across workers.

    Args:
        seed: Base random seed.

    Returns:
        A function suitable for passing as DataLoader's worker_init_fn.
    """
    def worker_init_fn(worker_id: int) -> None:
        set_seed(seed + worker_id, deterministic=True)

    return worker_init_fn