"""Noise reduction. Callers pass method and kernel_size (e.g. from contest defaults)."""

import numpy as np
import cv2

from PIL import Image
from typing import Union

# Valid reduction methods
_VALID_METHODS = {'gaussian_blur', 'bilateral_filter', 'median_filter'}


def noise_reduction(
    image: Union[Image.Image, np.ndarray],
    method: str = "gaussian_blur",
    kernel_size: int = 5,
) -> Union[Image.Image, np.ndarray]:
    """
    Reduce noise in image using filtering.
    
    Args:
        image: PIL Image or numpy array.
        method: Reduction method ('gaussian_blur', 'bilateral_filter', 'median_filter').
        kernel_size: Kernel size for filtering (must be odd).
        
    Returns:
        Denoised image of the same type as input.
    """
    # Validate method
    if method not in _VALID_METHODS:
        raise ValueError(
            f"Invalid method '{method}'. Must be one of: {', '.join(_VALID_METHODS)}"
        )
    
    # Validate kernel size
    if kernel_size % 2 == 0:
        raise ValueError(f"kernel_size must be odd, got {kernel_size}")
    
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
    
    # Apply filtering
    if method == 'gaussian_blur':
        enhanced = cv2.GaussianBlur(img_array, (kernel_size, kernel_size), 0)
    elif method == 'bilateral_filter':
        enhanced = cv2.bilateralFilter(img_array, kernel_size, 75, 75)
    else:  # method == 'median_filter'
        enhanced = cv2.medianBlur(img_array, kernel_size)
    
    # Convert back to PIL if input was PIL
    if is_pil:
        return Image.fromarray(enhanced)
    return enhanced
