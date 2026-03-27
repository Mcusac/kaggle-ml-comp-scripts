"""Vision model factories.

Provides factory functions for instantiating vision model architectures.
Supports DINOv2 (HuggingFace) and timm-based models.

Dependencies: level_0, level_1, level_2, level_3.
"""

from .vision_model_factory import create_vision_model

__all__ = [
    "create_vision_model",
]