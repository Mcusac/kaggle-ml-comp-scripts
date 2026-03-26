"""Shared data structure base: JSON config loader, lazy JSON model registry."""

from .config_loader import JSONConfigLoader
from .json_model_registry import create_json_model_registry

__all__ = [
    "JSONConfigLoader",
    "create_json_model_registry",
]