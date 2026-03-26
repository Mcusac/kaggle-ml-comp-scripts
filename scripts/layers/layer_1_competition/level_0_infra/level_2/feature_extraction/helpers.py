"""Helpers for FeatureExtractionTrainer: config extraction and joint feature+target extraction."""

from typing import Any, Tuple

import numpy as np

from layers.layer_0_core.level_2 import FeatureExtractor

from layers.layer_1_competition.level_0_infra.level_0 import (
    get_dataset_type,
    get_feature_extraction_model_name,
    get_regression_model_type,
)
from layers.layer_1_competition.level_0_infra.level_1 import validate_feature_extraction_inputs


class FeatureExtractionConfigHelper:
    """Thin static-method class delegating to C0/C1 config and validation functions."""

    @staticmethod
    def validate_inputs(config: Any, device: Any) -> None:
        validate_feature_extraction_inputs(config, device)

    @staticmethod
    def extract_dataset_type(config: Any) -> str:
        return get_dataset_type(config)

    @staticmethod
    def extract_regression_model_type(config: Any) -> str:
        return get_regression_model_type(config)

    @staticmethod
    def extract_feature_extraction_model_name(config: Any) -> str:
        return get_feature_extraction_model_name(config)


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
