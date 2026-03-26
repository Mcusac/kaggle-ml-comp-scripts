"""Minimal val transform: Resize, ToTensor, Normalize(ImageNet); no TTA."""

from typing import Tuple

from torchvision.transforms import Compose, Normalize, Resize, ToTensor

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def build_minimal_val_transform(image_size: Tuple[int, int]):
    """Build transform: Resize -> ToTensor -> Normalize(ImageNet)."""
    return Compose([
        Resize(image_size),
        ToTensor(),
        Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])