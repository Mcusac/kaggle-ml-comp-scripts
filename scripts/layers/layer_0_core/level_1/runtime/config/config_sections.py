"""Configuration section formatting utilities."""

from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def format_config_section(
    title: str,
    config: Mapping[str, Any],
    width: int = 60
) -> str:
    """
    Format a configuration section with a title and a separator.
    
    Args:
        title: Section title
        config: Dictionary of configuration key-value pairs to display
                None values are skipped
    """
    lines = []
    separator = "=" * width

    lines.append(separator)
    lines.append(title)
    lines.append(separator)

    for key, value in config.items():
        if value is not None:
            lines.append(f"   {key}: {value}")

    lines.append(separator)
    return "\n".join(lines)


def log_config_section(title: str, config: Mapping[str, Any]) -> None:
    """
    Log a formatted configuration section with consistent header formatting.

    Args:
        title: Section title
        config: Dictionary of configuration key-value pairs to display
                None values are skipped
    """
    _logger.info(format_config_section(title, config))


def print_config_section(title: str, config: Mapping[str, Any], width: int = 60) -> None:
    """
    Print a formatted configuration section to stdout.

    Args:
        title: Section title
        config: Dictionary of configuration key-value pairs to display
                None values are skipped
        width: Separator width
    """
    print(format_config_section(title, config, width))