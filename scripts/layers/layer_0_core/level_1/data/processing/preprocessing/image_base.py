"""
Generic image preprocessing utilities.
"""

import cv2
import numpy as np

from typing import Tuple

from level_0 import get_logger

logger = get_logger(__name__)


def crop_relative_height(
    img: np.ndarray,
    keep_ratio: float,
) -> np.ndarray:
    """
    Crop image vertically by keeping top portion.

    Args:
        img: Image array (H, W, C)
        keep_ratio: Fraction of height to keep (0 < keep_ratio <= 1)

    Returns:
        Cropped image
    """
    if not (0 < keep_ratio <= 1.0):
        raise ValueError("keep_ratio must be in (0, 1]")

    h = img.shape[0]
    cutoff = int(h * keep_ratio)

    return img[:cutoff, :]


def inpaint_by_hsv_range(
    img: np.ndarray,
    lower: Tuple[int, int, int],
    upper: Tuple[int, int, int],
    kernel_size: int = 3,
    iterations: int = 2,
    radius: int = 3,
) -> np.ndarray:
    """
    Inpaint pixels in given HSV range.

    Args:
        img: RGB image
        lower: Lower HSV bound
        upper: Upper HSV bound
        kernel_size: Dilation kernel size
        iterations: Dilation iterations
        radius: Inpainting radius

    Returns:
        Inpainted image
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(
        hsv,
        np.array(lower),
        np.array(upper),
    )

    if kernel_size > 0 and iterations > 0:
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=iterations)

    if np.any(mask):
        img = cv2.inpaint(
            img,
            mask,
            radius,
            cv2.INPAINT_TELEA,
        )

    return img