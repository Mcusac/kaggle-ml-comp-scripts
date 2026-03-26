"""Batch execution utilities."""

from typing import Any, Tuple

from layers.layer_0_core.level_0 import extract_batch_data


def run_supervised_batch(
    model: Any,
    device: Any,
    criterion: Any,
    batch: Tuple,
) -> Tuple[Any, Any, Any]:
    """
    Run forward pass and compute loss for a batch.

    Returns:
        outputs, targets, loss
    """

    inputs, targets = extract_batch_data(batch, device)

    outputs = model(inputs)

    loss = None
    if targets is not None and criterion is not None:
        loss = criterion(outputs, targets)

    return outputs, targets, loss