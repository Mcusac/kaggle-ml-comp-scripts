"""
Centralized logging utilities.

Provides idempotent setup and module-level logger factory.
"""

import os
import sys
import logging

from typing import Optional

_LOGGING_CONFIGURED = False


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure root logger to stream to stdout with a simple, uniform format.
    Idempotent: safe to call multiple times.

    Args:
        level: Optional log level name (e.g., 'INFO', 'DEBUG'). If not provided,
               uses environment variable LOG_LEVEL or defaults to INFO.
    """
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    log_level_name = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level)
    root.addHandler(handler)

    _LOGGING_CONFIGURED = True


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger with the specified name and level.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def reset_logging() -> None:
    """Reset logging configuration (primarily for testing)."""
    global _LOGGING_CONFIGURED
    root = logging.getLogger()
    root.handlers.clear()
    _LOGGING_CONFIGURED = False


def get_isolated_logger(
    name: str,
    level: int = logging.INFO,
    namespace: Optional[str] = None,
) -> logging.Logger:
    """Get a logger isolated from the root handler.
    
    Args:
        name: Logger name.
        level: Logging level (default: INFO).
        namespace: Optional prefix for the logger name. If provided,
                   the logger is named '{namespace}.{name}'. If omitted,
                   the logger is named '{name}' only.
    """
    logger = logging.getLogger(f"{namespace}.{name}" if namespace else name)
    logger.setLevel(level)
    logger.propagate = False
    return logger