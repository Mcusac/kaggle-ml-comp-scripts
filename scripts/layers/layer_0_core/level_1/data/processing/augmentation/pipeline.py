"""Transform composition utilities."""

import torchvision.transforms as transforms

from typing import List, Optional

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def compose_transform_pipeline(
    pil_transforms: Optional[List] = None,
    tensor_transforms: Optional[List] = None,
    include_to_tensor: bool = True
) -> transforms.Compose:
    """
    Compose a complete transform pipeline from PIL and tensor transforms.
    
    Standard pipeline order:
    1. PIL Image transforms (preprocessing, augmentation)
    2. ToTensor (converts PIL Image to tensor)
    3. Tensor transforms (normalization, tensor augmentation)
    
    Args:
        pil_transforms: List of PIL Image transforms to apply before ToTensor.
        tensor_transforms: List of tensor transforms to apply after ToTensor.
        include_to_tensor: Whether to include ToTensor transform (default: True).
                          Set to False if ToTensor is already in pil_transforms.
        
    Returns:
        Compose transform with the complete pipeline.
    
    Example:
        >>> from torchvision.transforms import Resize, Normalize
        >>> pipeline = compose_transform_pipeline(
        ...     pil_transforms=[Resize(224)],
        ...     tensor_transforms=[Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]
        ... )
    """
    transform_list = []
    
    # Add PIL transforms
    if pil_transforms:
        transform_list.extend(pil_transforms)
        logger.debug(f"Added {len(pil_transforms)} PIL transforms")
    
    # Add ToTensor
    if include_to_tensor:
        transform_list.append(transforms.ToTensor())
        logger.debug("Added ToTensor")
    
    # Add tensor transforms
    if tensor_transforms:
        transform_list.extend(tensor_transforms)
        logger.debug(f"Added {len(tensor_transforms)} tensor transforms")
    
    logger.debug(f"Composed transform pipeline with {len(transform_list)} total transforms")
    
    return transforms.Compose(transform_list)
