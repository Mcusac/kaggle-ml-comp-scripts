"""Image resizing utilities for transform pipelines."""

import torchvision.transforms as transforms

from PIL import Image
from typing import Union, Tuple

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def resize(
    image: Image.Image,
    size: Union[int, Tuple[int, int]],
    interpolation: int = Image.BILINEAR
) -> Image.Image:
    """
    Resize image to specified size.

    Args:
        image: PIL Image to resize.
        size: Target size. If int, creates square (size, size).
              If tuple (height, width), uses exact dimensions.
        interpolation: Interpolation method (default: Image.BILINEAR).

    Returns:
        Resized PIL Image with the specified dimensions.

    Raises:
        ValueError: If size is invalid (non-positive values).
        TypeError: If image is not a PIL Image or size has invalid type.
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"image must be PIL Image, got {type(image)}")

    if isinstance(size, int):
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
        size = (size, size)
    elif isinstance(size, tuple):
        if len(size) != 2:
            raise ValueError(f"size tuple must have length 2, got {size}")
        height, width = size
        if height <= 0 or width <= 0:
            raise ValueError(f"size dimensions must be positive, got {size}")
    else:
        raise TypeError(
            f"size must be int or tuple (int, int), got {type(size)}"
        )

    return image.resize(size, interpolation)


def get_resize_transform(
    size: Union[int, Tuple[int, int]],
    interpolation: int = Image.BILINEAR
) -> transforms.Resize:
    """
    Get a torchvision Resize transform for use in transform pipelines.

    Args:
        size: Target size. If int, creates square (size, size).
              If tuple (height, width), uses exact dimensions.
        interpolation: Interpolation method (default: Image.BILINEAR).

    Returns:
        Resize transform instance for torchvision transform pipelines.
    """
    if isinstance(size, int):
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
    elif isinstance(size, tuple):
        if len(size) != 2:
            raise ValueError(f"size tuple must have length 2, got {size}")
        height, width = size
        if height <= 0 or width <= 0:
            raise ValueError(f"size dimensions must be positive, got {size}")
    else:
        raise TypeError(
            f"size must be int or tuple (int, int), got {type(size)}"
        )

    return transforms.Resize(size, interpolation=interpolation)
