"""Configuration value extraction utilities.

Provides dot-notation path traversal over config objects and dicts,
enabling uniform access regardless of whether config is an object or dict.
"""

from typing import Any, Dict, Union


def get_config_value(
    config: Union[Any, Dict[str, Any]],
    path: str,
    default: Any = None,
    required: bool = False,
) -> Any:
    """
    Extract a config value using a dot-notation path.

    Traverses nested object attributes and dict keys interchangeably.

    Args:
        config:   Configuration object or dict.
        path:     Dot-separated key path (e.g. 'model.name', 'training.lr').
        default:  Value returned if the path is not found.
        required: If True, raises ValueError instead of returning default.

    Returns:
        The value at the given path, or default if not found.

    Raises:
        ValueError: If required is True and the path cannot be resolved.

    Examples:
        >>> get_config_value(config, "model.name", default="resnet50")
        >>> get_config_value(cfg_dict, "training.learning_rate", required=True)
    """
    if config is None:
        if required:
            raise ValueError(f"config cannot be None (required path: {path})")
        return default

    segments = path.split(".")
    current = config

    for i, segment in enumerate(segments):
        if current is None:
            if required:
                raise ValueError(
                    f"Cannot traverse path '{path}': segment {i} is None"
                )
            return default

        if isinstance(current, dict):
            if segment not in current:
                if required:
                    raise ValueError(
                        f"Key '{segment}' not found in path '{path}'"
                    )
                return default
            current = current[segment]
        else:
            if not hasattr(current, segment):
                if required:
                    raise ValueError(
                        f"Attribute '{segment}' not found in path '{path}'"
                    )
                return default
            current = getattr(current, segment)

    return current