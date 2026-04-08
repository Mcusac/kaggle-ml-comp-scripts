"""Vision model registry and config helpers. Uses level_5.

Config file `level_6/config/default_configs.json` is optional. If missing,
create_json_model_registry returns an empty registry (get_config returns {},
list_vision_models returns []). Add the file to register vision model configs.
"""

from pathlib import Path

from level_5 import create_json_model_registry

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "default_configs.json"
_get_config, _list_models, _get_all = create_json_model_registry(_CONFIG_PATH)


def get_vision_model_config(model_name: str):
    """Return config dict for a vision model by name."""
    return _get_config(model_name)


def list_vision_models():
    """Return list of registered vision model names."""
    return _list_models()


def __getattr__(name: str):
    if name == "VISION_MODELS":
        return _get_all()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
