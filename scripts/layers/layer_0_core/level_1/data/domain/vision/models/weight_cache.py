"""Weight cache resolution for offline and Kaggle environments."""

import os
import socket
from pathlib import Path
from typing import Optional, Tuple

from layers.layer_0_core.level_0 import is_kaggle, get_logger

_logger = get_logger(__name__)

_KAGGLE_WEIGHT_DIRS = [
    Path("/kaggle/input/model-weights"),
    Path("/kaggle/input/weights"),
    Path("/kaggle/input/pretrained-weights"),
]


def _check_internet_connection() -> bool:
    """Return True if an outbound internet connection is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        _logger.debug("Internet connection detected")
        return True
    except OSError:
        _logger.warning("No internet connection detected")
        return False


def configure_huggingface_cache(cache_dir: Path) -> None:
    """Point HuggingFace cache environment variables at cache_dir."""
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(cache_dir)
    _logger.info("Configured HuggingFace cache: %s", cache_dir)


def resolve_offline_weight_cache() -> Tuple[Optional[Path], bool]:
    """
    Detect the runtime environment and locate any available offline weights.

    Returns:
        (cache_path, has_internet) where cache_path is the first non-empty
        weight directory found (or None), and has_internet indicates whether
        an outbound connection is reachable.
    """
    has_internet = _check_internet_connection()

    if not is_kaggle():
        return None, has_internet

    for weight_dir in _KAGGLE_WEIGHT_DIRS:
        if weight_dir.exists() and any(weight_dir.iterdir()):
            _logger.info("Found Kaggle weight directory: %s", weight_dir)
            return weight_dir, has_internet

    return None, has_internet