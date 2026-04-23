"""Image normalization using ImageNet statistics."""

import torchvision.transforms as transforms

from typing import Any, Tuple

from layers.layer_0_core.level_0 import get_logger, get_torch, IMAGENET_MEAN, IMAGENET_STD

_torch = get_torch()
_logger = get_logger(__name__)


def normalize(
    tensor: Any,
    mean: Tuple[float, float, float] = IMAGENET_MEAN,
    std: Tuple[float, float, float] = IMAGENET_STD
) -> Any:
    """
    Normalize tensor using mean and standard deviation per channel.

    Args:
        tensor: Input tensor (C, H, W) or (B, C, H, W), range [0, 1].
        mean: Mean per channel (default: ImageNet mean).
        std: Std per channel (default: ImageNet std).

    Returns:
        Normalized tensor of the same shape.
    """
    if not isinstance(tensor, _torch.Tensor):
        raise TypeError(f"tensor must be torch.Tensor, got {type(tensor)}")
    if len(mean) != 3:
        raise ValueError(f"mean must be a tuple of length 3, got {mean}")
    if len(std) != 3:
        raise ValueError(f"std must be a tuple of length 3, got {std}")
    if any(s <= 0 for s in std):
        raise ValueError(f"std values must be positive, got {std}")

    normalize_transform = transforms.Normalize(mean=mean, std=std)
    return normalize_transform(tensor)


def get_normalize_transform(
    mean: Tuple[float, float, float] = IMAGENET_MEAN,
    std: Tuple[float, float, float] = IMAGENET_STD
) -> Any:
    """
    Get a torchvision Normalize transform for use in transform pipelines.

    Args:
        mean: Mean per channel (default: ImageNet mean).
        std: Std per channel (default: ImageNet std).

    Returns:
        Normalize transform instance.
    """
    if len(mean) != 3:
        raise ValueError(f"mean must be a tuple of length 3, got {mean}")
    if len(std) != 3:
        raise ValueError(f"std must be a tuple of length 3, got {std}")
    if any(s <= 0 for s in std):
        raise ValueError(f"std values must be positive, got {std}")

    return transforms.Normalize(mean=mean, std=std)
