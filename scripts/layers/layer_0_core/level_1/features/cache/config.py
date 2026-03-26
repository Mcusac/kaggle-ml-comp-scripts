"""Runtime configuration for the feature cache: path provider and model ID map.

The contest layer must call set_feature_cache_path_provider() and
set_model_id_map() at startup before any cache operations that depend on them.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from level_0 import get_logger, is_kaggle

logger = get_logger(__name__)

_feature_cache_path_provider: Optional[Callable[[], Any]] = None
_model_id_map: Optional[Dict[str, str]] = None


def set_feature_cache_path_provider(provider: Optional[Callable[[], Any]]) -> None:
    """Register the path provider for the feature cache.

    Args:
        provider: Callable returning an object with .input_base and .working_base
                  Path attributes. Pass None to revert to default paths.
    """
    global _feature_cache_path_provider
    _feature_cache_path_provider = provider


def set_model_id_map(model_id_map: Optional[Dict[str, str]]) -> None:
    """Register the model name → model_id mapping.

    Must be called by the contest layer at startup before any filename
    resolution that requires model name lookup.

    Args:
        model_id_map: Dict mapping model_name → model_id string.
    """
    global _model_id_map
    _model_id_map = model_id_map


def get_cache_base_paths() -> Tuple[Path, Path]:
    """Return (input_base, working_base) for the feature cache.

    Uses the registered path provider if set; falls back to local defaults.
    """
    if _feature_cache_path_provider is not None:
        paths = _feature_cache_path_provider()
        return paths.input_base, paths.working_base
    return Path("features_cache") / "input", Path("features_cache") / "working"


def get_model_name_from_model_id(model_id: str) -> str:
    """Reverse-look up the model name for a given model_id.

    Raises:
        RuntimeError: If set_model_id_map() has not been called.
        ValueError: If model_id is not present in the registered map.
    """
    if _model_id_map is None:
        raise RuntimeError(
            "model_id_map not set. Contest layer must call set_model_id_map() at startup."
        )
    for model_name, mapped_id in _model_id_map.items():
        if mapped_id == model_id:
            return model_name
    available_ids = ", ".join(sorted(set(_model_id_map.values())))
    raise ValueError(
        f"Model ID {model_id!r} not found in model_id_map. Available model IDs: {available_ids}"
    )


def get_metadata_dir() -> Optional[Path]:
    """Resolve the combo metadata directory from the registered path provider.

    Returns None if the provider is not registered or the directory cannot
    be determined. The contest layer is responsible for registering a provider
    that exposes metadata_dir or kaggle_metadata_dataset_name.

    Returns:
        Path to the metadata directory, or None.
    """
    if _feature_cache_path_provider is None:
        return None

    paths = _feature_cache_path_provider()

    if getattr(paths, "metadata_dir", None) is not None:
        return paths.metadata_dir

    kaggle_name = getattr(paths, "kaggle_metadata_dataset_name", None)
    if kaggle_name and is_kaggle():
        return Path("/kaggle/input") / kaggle_name

    return None