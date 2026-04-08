"""
Generic training loop executor.

Framework layer: callback-based epoch execution.
"""

from typing import Any, Callable, Optional

from level_0 import get_torch

torch = get_torch()
DataLoader = torch.utils.data.DataLoader if torch is not None else None


def train_one_epoch(
    train_loader: DataLoader,
    batch_processor: Callable[[Any], "torch.Tensor"],
    optimizer: torch.optim.Optimizer,
    scaler: Optional[Any] = None,
    use_tqdm: bool = False,
    tqdm_desc: Optional[str] = None,
) -> float:
    """
    Execute one training epoch using a caller-defined batch processor.

    Use when training logic is custom:
      - multi-input models
      - custom losses
      - AMP
      - non-(X, y) datasets

    batch_processor(batch) -> scalar loss tensor
    """

    if len(train_loader) == 0:
        raise ValueError("train_loader cannot be empty")

    total_loss = 0.0
    num_batches = 0

    iterator = train_loader

    if use_tqdm:
        from tqdm import tqdm
        iterator = tqdm(train_loader, desc=tqdm_desc or "Train")

    for batch in iterator:
        loss = batch_processor(batch)

        if torch.isnan(loss):
            raise RuntimeError("NaN loss detected during training")

        optimizer.zero_grad()

        if scaler:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    if num_batches == 0:
        raise ValueError("No batches processed")

    return total_loss / num_batches