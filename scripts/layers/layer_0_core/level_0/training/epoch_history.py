"""Epoch history entry construction."""

import numpy as np

from typing import Any, Dict, Optional


def create_history_entry(
    *,
    epoch: int,
    train_loss: float,
    val_loss: float,
    primary_metric_name: str,
    primary_metric_value: float,
    optimizer: Optional[Any],
    per_target_scores: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Build a history record for one training epoch.

    Metric-agnostic: the caller names the primary metric and provides its value.
    The contest or trainer layer is responsible for computing the metric (e.g.
    weighted R², accuracy, F1) and passing it in.

    Args:
        epoch:                Zero-based epoch index.
        train_loss:           Mean training loss for the epoch.
        val_loss:             Mean validation loss for the epoch.
        primary_metric_name:  Name of the primary tracking metric (e.g. "weighted_r2",
                              "accuracy", "f1"). Used as the dict key.
        primary_metric_value: Value of the primary metric for this epoch.
        optimizer:            Active optimizer, or None. When provided, the current
                              learning rate is read from param_groups[0]['lr'].
        per_target_scores:    Optional per-target breakdown as a numpy array (e.g.
                              per-target R² for multi-output regression). Stored as
                              a list. Pass None if not applicable.

    Returns:
        Dict with keys: epoch, train_loss, val_loss, <primary_metric_name>,
        per_target_scores (list or None), lr (float or None).
    """
    lr: Optional[float] = None
    if optimizer is not None:
        lr = optimizer.param_groups[0]["lr"]

    entry: Dict[str, Any] = {
        "epoch":      epoch,
        "train_loss": train_loss,
        "val_loss":   val_loss,
        primary_metric_name: primary_metric_value,
        "per_target_scores": per_target_scores.tolist() if per_target_scores is not None else None,
        "lr":         lr,
    }

    return entry