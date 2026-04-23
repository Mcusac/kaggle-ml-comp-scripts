"""Blurring augmentations. Callers pass params (e.g. from contest transform_defaults)."""

import torchvision.transforms as transforms

from typing import Tuple, Union

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def get_blur_transform(
    kernel_size: Union[int, Tuple[int, int]] = 3,
    sigma: Tuple[float, float] = (0.1, 2.0),
    p: float = 1.0,
) -> transforms.GaussianBlur:
    """
    Get Gaussian blur transform. When p < 1, wraps in RandomApply.
    Caller passes kernel_size and sigma (contest may use its defaults).
    """
    if isinstance(kernel_size, int):
        if kernel_size <= 0:
            raise ValueError(f"kernel_size must be positive, got {kernel_size}")
        if kernel_size % 2 == 0:
            kernel_size += 1
            _logger.debug("kernel_size was even, adjusted to %s", kernel_size)
    elif isinstance(kernel_size, tuple):
        if len(kernel_size) != 2:
            raise ValueError(f"kernel_size tuple must have length 2, got {kernel_size}")
        kernel_size = tuple(k + 1 if k % 2 == 0 else k for k in kernel_size)
    else:
        raise TypeError(f"kernel_size must be int or tuple, got {type(kernel_size)}")

    if len(sigma) != 2:
        raise ValueError(f"sigma must be a tuple of length 2, got {sigma}")
    if sigma[0] < 0 or sigma[1] < 0:
        raise ValueError(f"sigma values must be non-negative, got {sigma}")
    if sigma[0] > sigma[1]:
        raise ValueError(f"sigma[0] must be <= sigma[1], got {sigma}")

    t = transforms.GaussianBlur(kernel_size=kernel_size, sigma=sigma)
    if p < 1.0:
        return transforms.RandomApply([t], p=p)
    return t
