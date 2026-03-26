"""
Configuration helpers for feature extraction trainer.

Uses level_2.get_required_config_value for required keys; contest-specific
keys remain here.
"""

from typing import Any, Dict, Union

from layers.layer_0_core.level_0 import get_config_value
from layers.layer_0_core.level_2 import get_required_config_value

ConfigLike = Union[Any, Dict[str, Any]]


def get_feature_extraction_mode(config: ConfigLike) -> bool:
    return get_config_value(
        config,
        "model.feature_extraction_mode",
        default=False,
    )


def get_dataset_type(config: ConfigLike) -> str:
    return get_config_value(
        config,
        "data.dataset_type",
        default="split",
    )


def get_regression_model_type(config: ConfigLike) -> str:
    return get_required_config_value(
        config,
        "model.regression_model_type",
        error_msg="FeatureExtractionTrainer requires regression_model_type",
    )


def get_feature_extraction_model_name(config: ConfigLike) -> str:
    return get_required_config_value(
        config,
        "model.feature_extraction_model_name",
        error_msg="FeatureExtractionTrainer requires feature_extraction_model_name",
    )
