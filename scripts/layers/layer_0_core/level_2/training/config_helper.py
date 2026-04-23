"""
Generic configuration helper for trainers.

Framework layer: provides extraction logic without
domain-specific defaults.
"""

from typing import Dict, Optional, Tuple, Union, Any

from layers.layer_0_core.level_0 import get_logger, get_config_value
from layers.layer_0_core.level_1 import setup_mixed_precision

_logger = get_logger(__name__)


def get_required_config_value(
    config: Union[Any, Dict[str, Any]],
    key: str,
    *,
    error_msg: str,
) -> Any:
    """
    Get a required config value or raise with a custom message.

    Args:
        config: Configuration object or dict.
        key: Dot-separated path (e.g. 'model.regression_model_type').
        error_msg: Message used when the value is missing or falsy.

    Returns:
        The value at the given path.

    Raises:
        ValueError: If the value is missing or falsy.
    """
    value = get_config_value(config, key, default=None)
    if not value:
        raise ValueError(error_msg)
    return value


# ------------------------------------------------------------------
# Generic extraction
# ------------------------------------------------------------------

def extract_config_settings(
    config: Union[Any, Dict[str, Any]],
    num_primary_targets: Optional[int],
    model_name: Optional[str],
    image_size: Optional[Tuple[int, int]],
) -> tuple[Optional[int], Optional[str], Optional[Tuple[int, int]]]:
    """
    Extract basic training settings from config.

    No domain defaults are applied. Callers must provide
    fallbacks if required.

    Returns:
        (num_primary_targets, model_name, image_size)
    """

    # num targets
    if num_primary_targets is not None:
        extracted_num_targets = num_primary_targets
    else:
        primary_targets = get_config_value(
            config,
            "primary_targets",
            default=None,
        )
        extracted_num_targets = (
            len(primary_targets) if primary_targets else None
        )

    # model name
    extracted_model_name = model_name or get_config_value(
        config,
        "model.name",
        default=None,
    )

    # image size
    extracted_image_size = image_size or get_config_value(
        config,
        "data.image_size",
        default=None,
    )

    return (
        extracted_num_targets,
        extracted_model_name,
        extracted_image_size,
    )


# ------------------------------------------------------------------
# ConfigHelper class (for contest subclasses)
# ------------------------------------------------------------------


class ConfigHelper:
    """
    Base config helper with static methods for extraction and setup.
    Contest-specific helpers (e.g. ContestConfigHelper) subclass this.
    """

    @staticmethod
    def extract_config_settings(
        config: Union[Any, Dict[str, Any]],
        num_primary_targets: Optional[int],
        model_name: Optional[str],
        image_size: Optional[Tuple[int, int]],
    ) -> tuple[Optional[int], Optional[str], Optional[Tuple[int, int]]]:
        """Extract basic training settings from config. No domain defaults."""
        return extract_config_settings(config, num_primary_targets, model_name, image_size)

    @staticmethod
    def setup_mixed_precision(
        config: Union[Any, Dict[str, Any]],
        model_name: Optional[str],
        device: Any,
    ) -> tuple[bool, Optional[Any]]:
        """Set up mixed precision. Delegates to level_1 setup."""
        return setup_mixed_precision(config, device)


# ------------------------------------------------------------------
# Generic accessor
# ------------------------------------------------------------------

def get_training_config_value(
    config: Union[Any, Dict[str, Any]],
    key: str,
    default: Any,
) -> Any:
    """Get a training config value."""
    return get_config_value(config, f"training.{key}", default=default)