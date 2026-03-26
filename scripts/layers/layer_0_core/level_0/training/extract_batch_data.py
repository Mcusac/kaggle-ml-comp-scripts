"""Batch extraction utilities."""

from typing import Tuple, Optional, Union, Any


def extract_batch_data(
    batch: Union[Any, Tuple, list],
    device: Any
) -> Tuple[Any, Optional[Any]]:
    """
    Extract model inputs and targets from a batch and move to device.

    Supports:
      (images, targets)
      (left_img, right_img, targets)
      images only
    """

    if isinstance(batch, (list, tuple)):

        # standard supervised
        if len(batch) == 2:
            images, targets = batch
            return images.to(device), targets.to(device)

        # dual-input / split dataset
        if len(batch) == 3:
            left_img, right_img, targets = batch
            inputs = (left_img.to(device), right_img.to(device))
            return inputs, targets.to(device)

    # images only
    if not hasattr(batch, "to"):
        raise TypeError(f"Batch of type {type(batch)} has no .to() method; cannot move to device")
    return batch.to(device), None