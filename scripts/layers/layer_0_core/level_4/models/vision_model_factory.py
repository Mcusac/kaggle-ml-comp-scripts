"""Model factory for creating vision models. Uses level_1 and level_2 vision models."""

from typing import Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import BaseVisionModel
from level_2 import DINOv2Model
from level_3 import TimmModel

logger = get_logger(__name__)


def create_vision_model(
    model_name: str,
    num_classes: int,
    pretrained: bool = True,
    input_size: Optional[Tuple[int, int]] = None,
    **kwargs
) -> BaseVisionModel:
    """
    Factory function to create vision models.

    Args:
        model_name: Model architecture name (e.g., 'efficientnet_b0', 'resnet50', 'dinov2-base')
        num_classes: Number of output classes/targets
        pretrained: Whether to use pretrained weights (default: True)
        input_size: Optional input size override as (height, width) tuple
        **kwargs: Additional model-specific arguments:
            - use_tiles (bool): For DINOv2, whether to use tile-based processing
            - tile_grid_size (int): For DINOv2, grid size for tile extraction

    Returns:
        Vision model instance

    Raises:
        ValueError: If model_name is not supported

    Examples:
        >>> model = create_vision_model('efficientnet_b0', num_classes=5)
        >>> model = create_vision_model('dinov2-base', num_classes=5, input_size=(518, 518))
        >>> model = create_vision_model('dinov2-base', num_classes=5, use_tiles=True)
    """
    model_name_lower = model_name.lower()

    logger.info(f"Creating vision model: {model_name} (num_classes={num_classes}, pretrained={pretrained})")

    # DINOv2 models (HuggingFace format)
    if 'dinov2' in model_name_lower:
        # Map short names to HuggingFace model IDs
        if model_name_lower in ['dinov2-small', 'dinov2_small', 'dinov2-s']:
            hf_model_name = 'facebook/dinov2-small'
        elif model_name_lower in ['dinov2-base', 'dinov2_base', 'dinov2-b']:
            hf_model_name = 'facebook/dinov2-base'
        elif model_name_lower in ['dinov2-large', 'dinov2_large', 'dinov2-l']:
            hf_model_name = 'facebook/dinov2-large'
        elif model_name_lower in ['dinov2-giant', 'dinov2_giant', 'dinov2-g']:
            hf_model_name = 'facebook/dinov2-giant'
        else:
            hf_model_name = model_name

        logger.info(f"Using HuggingFace DINOv2 model: {hf_model_name}")

        return DINOv2Model(
            model_name=hf_model_name,
            pretrained=pretrained,
            num_classes=num_classes,
            input_size=input_size,
            **kwargs
        )

    # Timm models (covers EfficientNet, ResNet, ViT, etc.)
    else:
        logger.info(f"Using timm model: {model_name}")

        return TimmModel(
            model_name=model_name,
            pretrained=pretrained,
            num_classes=num_classes,
            input_size=input_size,
            **kwargs
        )