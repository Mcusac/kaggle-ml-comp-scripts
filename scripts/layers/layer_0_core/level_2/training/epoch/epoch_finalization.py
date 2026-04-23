"""Epoch-level orchestration helpers."""

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import step_scheduler, create_history_entry
from layers.layer_0_core.level_1 import log_epoch_progress


def finalize_epoch(
    *,
    epoch: int,
    num_epochs: int,
    train_loss: float,
    val_loss: float,
    metric_name: str,
    metric_value: float,
    per_target_scores: List[float],
    config: Any,
    scheduler: Any,
    optimizer: Any,
) -> Dict[str, Any]:
    """Step scheduler, log progress, and return a history entry for this epoch.

    Args:
        epoch: Zero-based epoch index.
        num_epochs: Total number of epochs.
        train_loss: Mean training loss for the epoch.
        val_loss: Mean validation loss for the epoch.
        metric_name: Name of the primary tracking metric (e.g. "weighted_r2").
        metric_value: Value of the primary tracking metric.
        per_target_scores: Per-target metric breakdown (e.g. per-target R²).
        config: Training config passed to step_scheduler.
        scheduler: LR scheduler to step.
        optimizer: Active optimizer (used for LR logging).

    Returns:
        History entry dict for this epoch.
    """
    step_scheduler(scheduler, config, metric_value, val_loss)
    log_epoch_progress(
        epoch=epoch,
        num_epochs=num_epochs,
        train_loss=train_loss,
        val_loss=val_loss,
        metric_name=metric_name,
        metric_value=metric_value,
        optimizer=optimizer,
    )
    return create_history_entry(
        epoch=epoch,
        train_loss=train_loss,
        val_loss=val_loss,
        primary_metric_name=metric_name,
        primary_metric_value=metric_value,
        per_target_scores=per_target_scores,
        optimizer=optimizer,
    )