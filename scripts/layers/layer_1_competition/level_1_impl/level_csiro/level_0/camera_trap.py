"""
Camera trap image cleaning.

Removes date stamps and bottom artifacts. CSIRO camera-trap domain.
"""

import numpy as np

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import ImageCleaningConfig, clean_image_with_config

logger = get_logger(__name__)

ORANGE_LOWER = (5, 150, 150)
ORANGE_UPPER = (25, 255, 255)
BOTTOM_ARTIFACT_RATIO = 0.90

_CAMERA_TRAP_CONFIG = ImageCleaningConfig(
    crop_keep_ratio=BOTTOM_ARTIFACT_RATIO,
    hsv_lower=ORANGE_LOWER,
    hsv_upper=ORANGE_UPPER,
    kernel_size=3,
    iterations=2,
    inpaint_radius=3,
)


def clean_camera_trap_image(img: np.ndarray) -> np.ndarray:
    """Clean camera trap image (remove date stamps and bottom artifacts)."""
    return clean_image_with_config(img, _CAMERA_TRAP_CONFIG)


def clean_camera_trap_batch(images: list[np.ndarray]) -> list[np.ndarray]:
    """Clean batch of camera trap images."""
    return [clean_camera_trap_image(img) for img in images]
