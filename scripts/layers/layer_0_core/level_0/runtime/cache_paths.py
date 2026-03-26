"""Derived cache paths. Caller passes cache_dir and optional overrides."""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class DerivedCachePaths:
    """Resolved cache directory paths derived from base cache_dir and optional overrides."""
    feature_cache_dir: str  # Resolved path to feature cache (default: cache_dir/features)
    model_cache_dir: str  # Resolved path to model cache (default: cache_dir/models)


def derive_cache_paths(
    cache_dir: Union[str, Path],
    feature_cache_dir: Optional[Union[str, Path]] = None,
    model_cache_dir: Optional[Union[str, Path]] = None,
) -> DerivedCachePaths:
    """
    Compute feature and model cache paths. Contest or orchestration passes cache_dir
    and optional overrides; level_1 does not depend on contest config.
    """
    cache = Path(cache_dir)
    feature_cache = str(Path(feature_cache_dir) if feature_cache_dir is not None else cache / "features")
    model_cache = str(Path(model_cache_dir) if model_cache_dir is not None else cache / "models")
    return DerivedCachePaths(feature_cache_dir=feature_cache, model_cache_dir=model_cache)
