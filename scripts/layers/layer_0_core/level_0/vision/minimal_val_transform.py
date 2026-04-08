"""Minimal val transform: Resize, ToTensor, Normalize(ImageNet); no TTA."""

from typing import Tuple

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def build_minimal_val_transform(image_size: Tuple[int, int]):
    """Build transform: Resize -> ToTensor -> Normalize(ImageNet)."""
    try:
        from torchvision.transforms import Compose, Normalize, Resize, ToTensor
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "torchvision is required for build_minimal_val_transform(). "
            "Install torchvision or avoid vision transforms."
        ) from e
    return Compose([
        Resize(image_size),
        ToTensor(),
        Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])