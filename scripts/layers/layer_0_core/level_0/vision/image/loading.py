"""PIL-based image loading for vision pipelines.
Generic image loading utilities."""

import cv2
import numpy as np

from PIL import Image
from pathlib import Path
from typing import Union



def load_image_pil(path: Path, convert_rgb: bool = True) -> Image.Image:
    """Load image with optional RGB conversion. No validation or error handling."""
    image = Image.open(path)
    if convert_rgb and image.mode != "RGB":
        image = image.convert("RGB")
    return image


def load_image_rgb(
    image: Union[np.ndarray, Image.Image, str, Path]
) -> np.ndarray:
    """
    Normalize input into RGB numpy array.

    Supports:
        - file paths
        - PIL images
        - numpy arrays
    """

    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        if img is None:
            raise ValueError(f"Could not load image: {image}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if isinstance(image, Image.Image):
        img = np.array(image)
    elif isinstance(image, np.ndarray):
        img = image.copy()
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")

    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    return img