"""Joint feature and target extraction for feature-extraction training."""

from typing import Any, Tuple

import numpy as np

from layers.layer_0_core.level_2 import FeatureExtractor


class FeatureExtractionHelper:
    """Wraps FeatureExtractor for joint feature and target extraction from a DataLoader."""

    def __init__(self, feature_extractor: FeatureExtractor, dataset_type: str) -> None:
        self._feature_extractor = feature_extractor
        self._dataset_type = dataset_type

    def extract_all_features(self, loader: Any) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features and targets from all batches. Returns (features, targets)."""
        return self._feature_extractor.extract_features_and_targets(
            loader, dataset_type=self._dataset_type
        )
