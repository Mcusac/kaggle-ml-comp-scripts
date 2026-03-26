"""Feature extraction utilities for two-stage training pipelines."""

import numpy as np

from typing import Tuple

from layers.layer_0_core.level_0 import get_torch
from level_2 import FeatureExtractor

torch = get_torch()
DataLoader = torch.utils.data.DataLoader


def extract_all_features(
    feature_extractor: FeatureExtractor,
    all_loader: DataLoader,
    dataset_type: str,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract features and targets from all batches in a DataLoader.

    Args:
        feature_extractor: Initialised FeatureExtractor to run inference with.
        all_loader: DataLoader containing all images to process.
        dataset_type: Batch layout — 'split' expects (left, right, targets),
                      any other value expects (images, targets).

    Returns:
        Tuple of (all_features, all_targets), both as float32 numpy arrays.
        all_features shape: (n_samples, feature_dim)
        all_targets shape:  (n_samples, n_targets)
    """
    all_features = feature_extractor.extract_features(
        all_loader,
        dataset_type=dataset_type,
    )
    all_targets = _extract_targets(all_loader, dataset_type)
    return all_features, all_targets


def _extract_targets(
    dataloader: DataLoader,
    dataset_type: str,
) -> np.ndarray:
    """
    Collect target tensors from every batch in a DataLoader.

    Args:
        dataloader: DataLoader whose batches contain a targets tensor.
        dataset_type: Batch layout — 'split' expects (left, right, targets),
                      any other value expects (images, targets).

    Returns:
        Float32 array of shape (n_samples, n_targets).
    """
    all_targets = []
    for batch in dataloader:
        if dataset_type == 'split':
            _, _, targets = batch
        else:
            _, targets = batch
        t = targets.cpu().numpy() if hasattr(targets, 'cpu') else np.array(targets)
        all_targets.append(t)
    return np.concatenate(all_targets, axis=0)