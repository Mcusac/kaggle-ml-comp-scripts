"""
Shared lazy-loaded JSON model registry.

Returns (get_config, list_models) that load from a domain-specific JSON path once.
Used by vision and tabular model_config to avoid duplicated loading/caching logic.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List

from layers.layer_0_core.level_4 import load_json


def create_json_model_registry(config_path: Path) -> tuple[
    Callable[[str], Dict[str, Any]],
    Callable[[], List[str]],
    Callable[[], Dict[str, Any]],
]:
    """
    Returns (get_config, list_models, get_all) that lazy-load from config_path.

    get_config(name) returns a copy of the config dict for that name, or {}.
    list_models() returns the list of registered model names/types.
    get_all() returns the full catalog dict (for VISION_MODELS / TABULAR_MODELS).
    """
    _cache: Dict[str, Any] | None = None

    def _load() -> Dict[str, Any]:
        nonlocal _cache
        if _cache is None:
            if config_path.exists():
                _cache = load_json(config_path)
            else:
                _cache = {}
        return _cache

    def get_config(name: str) -> Dict[str, Any]:
        models = _load()
        return dict(models.get(name, {}))

    def list_models() -> List[str]:
        return list(_load().keys())

    def get_all() -> Dict[str, Any]:
        return _load()

    return get_config, list_models, get_all
