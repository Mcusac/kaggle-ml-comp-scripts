"""Standard supervised PyTorch epoch templates.

For conventional supervised learning: (X, y) batches, single model,
single criterion, single optimizer.
"""

from typing import Optional
from tqdm import tqdm

from layers.layer_0_core.level_0 import get_torch
from layers.layer_0_core.level_1 import train_one_epoch, run_supervised_batch

torch = get_torch()
nn = torch.nn
DataLoader = torch.utils.data.DataLoader


def run_train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    scaler: Optional[object] = None,
    use_tqdm: bool = False,
) -> float:
    """
    Run one supervised training epoch for (X, y) datasets.

    For custom training logic, use the epoch executor directly.

    Args:
        model: Model to train.
        train_loader: Training DataLoader yielding (X, y) batches.
        optimizer: Optimizer.
        criterion: Loss function.
        device: Training device.
        scaler: Optional GradScaler for mixed-precision training.
        use_tqdm: Whether to show a tqdm progress bar.

    Returns:
        Average training loss for the epoch.
    """
    model.train()

    def batch_processor(batch):
        batch_X, batch_y = batch
        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)
        return criterion(model(batch_X), batch_y)

    return train_one_epoch(
        train_loader=train_loader,
        batch_processor=batch_processor,
        optimizer=optimizer,
        scaler=scaler,
        use_tqdm=use_tqdm,
        tqdm_desc="Train",
    )


def run_validate_epoch(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_tqdm: bool = False,
) -> float:
    """
    Run one supervised validation epoch for (X, y) datasets.

    Args:
        model: Model to evaluate.
        val_loader: Validation DataLoader yielding (X, y) batches.
        criterion: Loss function.
        device: Validation device.
        use_tqdm: Whether to show a tqdm progress bar.

    Returns:
        Average validation loss for the epoch.

    Raises:
        ValueError: If val_loader yields no batches.
    """
    model.eval()

    total_loss = 0.0
    num_batches = 0
    iterator = tqdm(val_loader, desc="Validate") if use_tqdm else val_loader

    with torch.no_grad():
        for batch in iterator:
            _, _, loss = run_supervised_batch(model, device, criterion, batch)
            total_loss += loss.item()
            num_batches += 1

    if num_batches == 0:
        raise ValueError("No batches processed")

    return total_loss / num_batches