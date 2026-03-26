"""Shared config extraction for vision transforms."""

from typing import Any, Optional, Tuple, Union


def get_image_size_from_config(config: Any) -> Optional[Union[int, Tuple[int, int]]]:
    """
    Extract image_size from config dict or object.

    Args:
        config: Configuration object or dict with image_size (or config.data.image_size).

    Returns:
        image_size as int or (height, width) tuple, or None if not set.
    """
    if config is None:
        return None
    if isinstance(config, dict):
        return config.get("image_size")
    if hasattr(config, "data") and hasattr(config.data, "image_size"):
        return config.data.image_size
    if hasattr(config, "image_size"):
        return config.image_size
    return None
