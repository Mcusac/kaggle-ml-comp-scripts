"""Feature cache management."""

from .config import (
    set_feature_cache_path_provider,
    set_model_id_map,
    get_cache_base_paths,
    get_model_name_from_model_id,
    get_metadata_dir,
)
from .filename import generate_feature_filename, parse_feature_filename

__all__ = [
    # Cache configuration — must be called at startup by contest layer
    "set_feature_cache_path_provider",
    "set_model_id_map",
    "get_cache_base_paths",
    "get_model_name_from_model_id",
    "get_metadata_dir",
    # Filename codec
    "generate_feature_filename",
    "parse_feature_filename",
]