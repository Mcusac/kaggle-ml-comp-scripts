"""DataLoader construction from Dataset."""

from typing import Any, Callable, Optional

from layers.layer_0_core.level_0 import get_torch


def create_dataloader_from_dataset(
    dataset: Any,
    batch_size: int,
    shuffle: bool = False,
    num_workers: int = 4,
    pin_memory: bool = True,
    worker_init_fn: Optional[Callable] = None,
    persistent_workers: Optional[bool] = None,
) -> Any:
    """
    Create DataLoader from any Dataset.

    Shared by train, validation, and test loaders.

    Args:
        dataset: PyTorch Dataset.
        batch_size: Batch size.
        shuffle: Whether to shuffle (default: False).
        num_workers: Number of data loading workers (default: 4).
        pin_memory: Whether to pin memory for faster GPU transfer (default: True).
        worker_init_fn: Optional worker init function for reproducibility.
        persistent_workers: If None, defaults to num_workers > 0.

    Returns:
        PyTorch DataLoader.
    """
    torch = get_torch()
    DataLoader = torch.utils.data.DataLoader

    if persistent_workers is None:
        persistent_workers = num_workers > 0

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        worker_init_fn=worker_init_fn if num_workers > 0 else None,
        persistent_workers=persistent_workers,
    )
