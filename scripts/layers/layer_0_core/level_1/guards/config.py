"""Configuration structure guards."""

from typing import Any

from layers.layer_0_core.level_0 import ConfigValidationError, get_config_value, get_torch


def validate_config_section_exists(
    config: Any,
    section_name: str,
    *,
    config_name: str = "config",
) -> None:
    """
    Ensure a configuration object contains a non-None section.

    Args:
        config: Configuration object
        section_name: Attribute name to check
        config_name: Name used in error message

    Raises:
        ConfigValidationError:
            - If config is None
            - If section does not exist
            - If section value is None
    """
    if config is None:
        raise ConfigValidationError(f"{config_name} cannot be None")

    if not hasattr(config, section_name):
        raise ConfigValidationError(
            f"{config_name}.{section_name} is missing"
        )

    if getattr(config, section_name) is None:
        raise ConfigValidationError(
            f"{config_name}.{section_name} cannot be None"
        )


def validate_feature_extraction_trainer_inputs(
    config: Any,
    device: Any,
    *,
    feature_extraction_mode_key: str = "model.feature_extraction_mode",
) -> None:
    """
    Validate config and device for feature extraction trainer.

    Args:
        config: Configuration object or dict.
        device: Must be torch.device.
        feature_extraction_mode_key: Config path for feature extraction flag.

    Raises:
        ConfigValidationError: If config is None or feature_extraction_mode is not True.
        TypeError: If device is not torch.device.
    """
    torch_mod = get_torch()
    if config is None:
        raise ConfigValidationError("config cannot be None")
    if not get_config_value(config, feature_extraction_mode_key, default=False):
        raise ConfigValidationError(
            "FeatureExtractionTrainer requires feature_extraction_mode=True"
        )
    if not isinstance(device, torch_mod.device):
        raise TypeError(f"device must be torch.device, got {type(device)}")