"""Split features and targets by fold assignment (numpy arrays)."""

import numpy as np

from typing import Tuple

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def split_features_by_fold(
    all_features: np.ndarray,
    all_targets: np.ndarray,
    fold_assignments: np.ndarray,
    current_fold: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split all features and targets by fold assignment.

    Args:
        all_features: All features array (N_total, feat_dim).
        all_targets: All targets array (N_total, num_targets).
        fold_assignments: Fold assignments array (N_total,) with values 0 to n_folds-1.
        current_fold: Current fold number to split for.

    Returns:
        Tuple of (train_features, val_features, train_targets, val_targets).
    """
    if all_features.shape[0] != all_targets.shape[0] or all_features.shape[0] != fold_assignments.shape[0]:
        raise ValueError(
            f"Array length mismatch: all_features={all_features.shape[0]}, "
            f"all_targets={all_targets.shape[0]}, fold_assignments={fold_assignments.shape[0]}"
        )
    if current_fold < 0:
        raise ValueError(f"current_fold must be >= 0, got {current_fold}")

    train_mask = fold_assignments != current_fold
    val_mask = fold_assignments == current_fold
    if not np.any(val_mask):
        raise ValueError(f"No samples found for fold {current_fold}")

    train_features = all_features[train_mask]
    val_features = all_features[val_mask]
    train_targets = all_targets[train_mask]
    val_targets = all_targets[val_mask]
    logger.debug(f"Split features for fold {current_fold}: train {train_features.shape}, val {val_features.shape}")
    return train_features, val_features, train_targets, val_targets
