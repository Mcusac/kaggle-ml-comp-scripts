"""Runtime setup logic for pipeline execution."""

from typing import Any, Dict

from layers.layer_0_core.level_0 import get_logger, is_kaggle
from layers.layer_0_core.level_1 import get_device_info

_logger = get_logger(__name__)


def setup_runtime_environment() -> Dict[str, Any]:
    """
    Orchestration-level runtime setup.

    Interprets hardware and environment facts and returns execution context.

    Returns:
        Dict with keys: is_kaggle, has_gpu, gpu_info.
    """
    kaggle = is_kaggle()
    _logger.info("Running on Kaggle: %s", kaggle)

    gpu_info = get_device_info()
    has_gpu = bool(gpu_info.get("cuda_available", False))

    if has_gpu:
        names = gpu_info.get("device_names", [])
        _logger.info(
            "GPU available: %s (count=%s)",
            names[0] if names else "Unknown",
            gpu_info.get("device_count", 0),
        )
    else:
        _logger.warning("No GPU detected — training will run on CPU")

    return {
        "is_kaggle": kaggle,
        "has_gpu": has_gpu,
        "gpu_info": gpu_info,
    }