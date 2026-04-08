"""
Composable image cleaning pipelines.
"""

import numpy as np

from dataclasses import dataclass
from typing import List, Optional, Tuple

from level_0 import get_logger
from level_1 import crop_relative_height, inpaint_by_hsv_range

logger = get_logger(__name__)


@dataclass
class ImageCleaningConfig:
    """
    Configuration for image cleaning.
    """

    crop_keep_ratio: Optional[float] = None

    hsv_lower: Optional[Tuple[int, int, int]] = None
    hsv_upper: Optional[Tuple[int, int, int]] = None

    kernel_size: int = 3
    iterations: int = 2
    inpaint_radius: int = 3


def clean_image_with_config(
    img: np.ndarray,
    config: ImageCleaningConfig,
) -> np.ndarray:
    """
    Clean image using configurable pipeline.
    """

    if config.crop_keep_ratio is not None:
        img = crop_relative_height(
            img,
            config.crop_keep_ratio,
        )

    if config.hsv_lower and config.hsv_upper:
        img = inpaint_by_hsv_range(
            img,
            lower=config.hsv_lower,
            upper=config.hsv_upper,
            kernel_size=config.kernel_size,
            iterations=config.iterations,
            radius=config.inpaint_radius,
        )

    return img


def clean_image_batch(
    images: List[np.ndarray],
    config: ImageCleaningConfig,
) -> List[np.ndarray]:
    """
    Clean batch using same config.
    """

    return [
        clean_image_with_config(img, config)
        for img in images
    ]