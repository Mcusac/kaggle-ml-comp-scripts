"""Contrast enhancement. Callers pass method (e.g. from contest defaults)."""

import numpy as np
import cv2

from PIL import Image
from typing import Union

from level_0 import get_logger

logger = get_logger(__name__)

# Valid enhancement methods
_VALID_METHODS = {'histogram_equalization', 'clahe'}


def contrast_enhancement(
    image: Union[Image.Image, np.ndarray],
    method: str = "histogram_equalization",
) -> Union[Image.Image, np.ndarray]:
    """
    Enhance image contrast using histogram equalization or CLAHE.
    
    Args:
        image: PIL Image or numpy array.
        method: Enhancement method ('histogram_equalization', 'clahe').
        
    Returns:
        Enhanced image of the same type as input.
    """
    # Validate method
    if method not in _VALID_METHODS:
        raise ValueError(
            f"Invalid method '{method}'. Must be one of: {', '.join(_VALID_METHODS)}"
        )
    
    # Convert PIL to numpy if needed
    if isinstance(image, Image.Image):
        img_array = np.array(image)
        is_pil = True
    else:
        img_array = np.asarray(image)
        is_pil = False
    
    # Ensure uint8
    if img_array.dtype != np.uint8:
        img_array = (img_array * 255).astype(np.uint8) if img_array.max() <= 1.0 else img_array.astype(np.uint8)
    
    # Apply enhancement
    if len(img_array.shape) == 2:
        # Grayscale
        if method == 'histogram_equalization':
            enhanced = cv2.equalizeHist(img_array)
        else:  # method == 'clahe'
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(img_array)
    elif len(img_array.shape) == 3:
        # RGB - apply to each channel
        enhanced = np.zeros_like(img_array)
        if method == 'histogram_equalization':
            for i in range(img_array.shape[2]):
                enhanced[:, :, i] = cv2.equalizeHist(img_array[:, :, i])
        else:  # method == 'clahe'
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            for i in range(img_array.shape[2]):
                enhanced[:, :, i] = clahe.apply(img_array[:, :, i])
    else:
        raise ValueError(f"Unsupported image shape: {img_array.shape}")
    
    # Convert back to PIL if input was PIL
    if is_pil:
        return Image.fromarray(enhanced)
    return enhanced
