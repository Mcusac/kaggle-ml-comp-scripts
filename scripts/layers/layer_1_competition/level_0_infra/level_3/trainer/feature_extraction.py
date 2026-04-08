"""Feature extraction trainer for two-stage training. Uses level_0–level_3 and level_5 (save_regression_model)."""

import re
import numpy as np

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from layers.layer_0_core.level_0 import ensure_dir, get_config_value, get_logger, get_torch
from layers.layer_0_core.level_1 import split_features_by_fold
from layers.layer_0_core.level_1.guards import validate_feature_extraction_trainer_inputs
from layers.layer_0_core.level_2 import FeatureExtractor, get_required_config_value
from layers.layer_0_core.level_3 import create_regression_model
from layers.layer_0_core.level_5 import save_regression_model

from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model
from layers.layer_1_competition.level_0_infra.level_2 import FeatureExtractionHelper

logger = get_logger(__name__)
torch = get_torch()
nn = torch.nn
DataLoader = torch.utils.data.DataLoader


class FeatureExtractionTrainer:
    """
    Two-stage trainer for feature extraction mode.

    Stage 1: Extract features from images using a feature extraction model
    Stage 2: Train a regression model (LGBM/XGB/Ridge) on the extracted features
    """

    def __init__(
        self,
        config: Union[Any, Dict[str, Any]],
        device: torch.device,
        feature_extraction_model: Optional[nn.Module] = None,
        regression_model_hyperparameters: Optional[Dict[str, Any]] = None,
        regression_only: bool = False,
        metric_calculator: Optional[Any] = None,
        num_primary_targets: Optional[int] = None,
    ):
        """Initialize FeatureExtractionTrainer. metric_calculator from contest context."""
        validate_feature_extraction_trainer_inputs(config, device)

        self.config = config
        self._num_primary_targets = num_primary_targets
        self.device = device
        self._metric_calculator = metric_calculator
        self.dataset_type = get_config_value(config, "data.dataset_type", default="split")
        self.regression_only = regression_only

        regression_model_type = get_required_config_value(
            config,
            "model.regression_model_type",
            error_msg="FeatureExtractionTrainer requires regression_model_type",
        )
        self.feature_extractor = self._setup_feature_extractor(
            config, device, feature_extraction_model, regression_only
        )
        self.regression_model = create_regression_model(
            regression_model_type,
            **(regression_model_hyperparameters or {})
        )

        self.feature_helper = FeatureExtractionHelper(self.feature_extractor, self.dataset_type)

        self.best_score = -float('inf')
        self.best_epoch = 0
        self.history: List[Dict] = []

    def _setup_feature_extractor(
        self,
        config: Union[Any, Dict[str, Any]],
        device: torch.device,
        feature_extraction_model: Optional[nn.Module],
        regression_only: bool
    ) -> Optional[FeatureExtractor]:
        """Setup feature extraction model."""
        if regression_only:
            return None

        feature_extraction_model_name = get_required_config_value(
            config,
            "model.feature_extraction_model_name",
            error_msg="FeatureExtractionTrainer requires feature_extraction_model_name",
        )

        if feature_extraction_model is None:
            feature_extraction_model = self._create_feature_extraction_model(
                feature_extraction_model_name
            )

        return FeatureExtractor(feature_extraction_model, device)

    def _create_feature_extraction_model(self, model_name: str) -> nn.Module:
        """Create feature extraction model from model name."""
        num_primary_targets = self._num_primary_targets
        if num_primary_targets is None and isinstance(self.config, dict):
            num_primary_targets = self.config.get("num_primary_targets")
        if num_primary_targets is None and hasattr(self.config, "primary_targets"):
            num_primary_targets = len(self.config.primary_targets)
        if num_primary_targets is None:
            num_primary_targets = 3  # Fallback for biomass-style contests; prefer explicit config

        return create_feature_extraction_model(
            model_name=model_name,
            num_primary_targets=num_primary_targets,
            device=self.device,
            image_size=None,
            pretrained=True
        )

    def extract_all_features(
        self,
        all_loader: DataLoader
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features and targets from all images."""
        logger.info("Extracting features from all images...")
        all_features, all_targets = self.feature_helper.extract_all_features(all_loader)
        logger.info(f"Extracted features: {all_features.shape}, targets: {all_targets.shape}")
        return all_features, all_targets

    def train(
        self,
        train_loader: Optional[DataLoader] = None,
        val_loader: Optional[DataLoader] = None,
        num_epochs: Optional[int] = None,
        save_dir: Optional[Path] = None,
        resume: bool = True,
        extract_features: bool = True,
        fold: Optional[int] = None,
        all_features: Optional[np.ndarray] = None,
        all_targets: Optional[np.ndarray] = None,
        fold_assignments: Optional[np.ndarray] = None
    ) -> List[Dict]:
        """Train regression model on extracted features."""
        if fold is None and save_dir is not None:
            fold_match = re.search(r'fold[_\s]?(\d+)', str(save_dir), re.IGNORECASE)
            if fold_match:
                fold = int(fold_match.group(1))

        if all_features is not None:
            if all_targets is None:
                raise ValueError("all_targets is required when all_features is provided")
            if fold_assignments is None:
                raise ValueError("fold_assignments is required when all_features is provided")
            if fold is None:
                raise ValueError("fold is required when using pre-extracted features")

            logger.info(f"Using pre-extracted features, splitting for fold {fold}...")
            train_features, val_features, train_targets, val_targets = split_features_by_fold(
                all_features, all_targets, fold_assignments, fold
            )
        else:
            if train_loader is None or val_loader is None:
                raise ValueError("train_loader and val_loader are required when all_features is not provided")

            logger.info("Extracting features from loaders...")
            train_features, train_targets = self.extract_all_features(train_loader)
            val_features, val_targets = self.extract_all_features(val_loader)

        logger.info(f"Features: train {train_features.shape}, val {val_features.shape}")
        logger.info(f"Targets: train {train_targets.shape}, val {val_targets.shape}")

        logger.info("Training regression model on extracted features...")
        self.regression_model.fit(train_features, train_targets)

        val_predictions = self.regression_model.predict(val_features)
        if self._metric_calculator is None:
            raise ValueError("metric_calculator is required for FeatureExtractionTrainer")
        weighted_r2, r2_scores = self._metric_calculator(val_predictions, val_targets, config=self.config)
        val_score = weighted_r2

        logger.info("Regression model training complete")
        logger.info(f"Validation Score: {val_score:.4f}")

        self.best_score = val_score
        self.best_epoch = 0

        if save_dir:
            ensure_dir(save_dir)
            save_regression_model(self.regression_model, save_dir)

        history_entry = {
            'epoch': 0,
            'train_loss': None,
            'val_loss': None,
            'val_score': val_score
        }
        self.history = [history_entry]

        return self.history
