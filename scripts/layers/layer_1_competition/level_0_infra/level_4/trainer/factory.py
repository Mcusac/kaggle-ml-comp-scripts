"""Trainer factory for creating appropriate trainer instances."""

from typing import Optional, Dict, Any, Union

from layers.layer_0_core.level_0 import get_config_value, get_logger
from layers.layer_0_core.level_5 import BaseModelTrainer

from layers.layer_1_competition.level_0_infra.level_0 import get_feature_extraction_mode
from layers.layer_1_competition.level_0_infra.level_3.trainer import FeatureExtractionTrainer

logger = get_logger(__name__)


def create_trainer(
    config: Any,
    device: Any,
    model: Optional[Any] = None,
    regression_model_hyperparameters: Optional[Dict[str, Any]] = None,
    regression_only: bool = False,
    metric_calculator: Optional[Any] = None,
) -> Union[BaseModelTrainer, FeatureExtractionTrainer]:
    """
    Create appropriate trainer based on config mode.

    If config.model.feature_extraction_mode is True, creates FeatureExtractionTrainer.
    Otherwise, creates BaseModelTrainer for end-to-end training.
    """
    if get_feature_extraction_mode(config):
        num_primary_targets = get_config_value(config, "num_primary_targets", default=None)
        if regression_only:
            logger.info("Creating FeatureExtractionTrainer (regression-only mode: features already extracted)")
        else:
            logger.info("Creating FeatureExtractionTrainer (two-stage: feature extraction + regression)")
        return FeatureExtractionTrainer(
            config,
            device,
            feature_extraction_model=None,
            regression_model_hyperparameters=regression_model_hyperparameters,
            regression_only=regression_only,
            metric_calculator=metric_calculator,
            num_primary_targets=num_primary_targets,
        )
    else:
        logger.info("Creating BaseModelTrainer (end-to-end training)")
        return BaseModelTrainer(config, device, model=model, metric_calculator=metric_calculator)
