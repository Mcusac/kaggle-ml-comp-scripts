"""
Generic epoch progress logging.
Framework-level: metric-agnostic.
"""

from typing import Optional

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def log_epoch_progress(
    *,
    epoch: int,
    num_epochs: int,
    train_loss: float,
    val_loss: float,
    metric_name: Optional[str],
    metric_value: Optional[float],
    optimizer,
    log_interval: int = 10,
) -> None:
    """
    Log training progress for an epoch.

    Args:
        metric_name: Name of primary metric (e.g. 'R2', 'Accuracy')
        metric_value: Value of primary metric
    """

    if optimizer is None:
        return

    if epoch % log_interval != 0 and epoch != num_epochs - 1:
        return

    current_lr = optimizer.param_groups[0]["lr"]

    parts = [
        f"Epoch [{epoch}/{num_epochs}]",
        f"Train Loss: {train_loss:.4f}",
        f"Val Loss: {val_loss:.4f}",
    ]

    if metric_name and metric_value is not None:
        parts.append(f"{metric_name}: {metric_value:.4f}")

    parts.append(f"LR: {current_lr:.6f}")

    _logger.info(", ".join(parts))


def log_epoch_progress_with_metric(
    *,
    epoch: int,
    num_epochs: int,
    train_loss: float,
    val_loss: float,
    metric_name: str,
    metric_value: float,
    optimizer,
    log_interval: int = 10,
) -> None:
    """
    Log epoch progress with a custom metric.

    Convenience wrapper for log_epoch_progress when metric_name/metric_value
    are known (e.g. "Weighted R²", weighted_r2).
    """
    log_epoch_progress(
        epoch=epoch,
        num_epochs=num_epochs,
        train_loss=train_loss,
        val_loss=val_loss,
        metric_name=metric_name,
        metric_value=metric_value,
        optimizer=optimizer,
        log_interval=log_interval,
    )