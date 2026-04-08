"""Model name to pretrained weights mapping.

This module provides shared model metadata (IDs, image sizes, pretrained paths).
The pretrained path defaults in _MODEL_NAME_TO_PRETRAINED assume Kaggle dataset
layout (e.g. /kaggle/input/dinov2/...). Contests using different layouts should
override via contest config or pass explicit paths to model creation.
"""

from typing import Dict, Optional, Tuple

from layers.layer_0_core.level_1 import set_model_id_map

# Model ID mapping for feature file naming
# Maps MODEL_NAME to 2-digit ID for feature filename generation
MODEL_ID_MAP: Dict[str, str] = {  # Injected into level_1.features.feature_cache via set_model_id_map()
    "dinov2_base": "01",
    "dinov2_large": "02",
    "timm_efficientnet_b3": "03",
    "siglip_so400m_patch14_384": "04",
}

def register_model_id_map(model_id_map: Optional[Dict[str, str]] = None) -> None:
    """
    Register the model name → ID mapping used by core feature-cache naming.

    This is intentionally an explicit call (no import-time side effects).
    Contests may override by calling this with their own mapping.
    """
    set_model_id_map(MODEL_ID_MAP if model_id_map is None else model_id_map)

# Mapping from MODEL_NAME to pretrained weights path/name.
# Defaults assume Kaggle dataset layout. Contests with different paths should override.
_MODEL_NAME_TO_PRETRAINED: Dict[str, str] = {
    # DINOv2 models (offline pretrained weights)
    "dinov2_base": "/kaggle/input/dinov2/pytorch/base/1",
    "dinov2_large": "/kaggle/input/dinov2/pytorch/large/1",
    # Timm models (model name strings)
    "timm_efficientnet_b3": "efficientnet_b3",
    # SigLIP models (HuggingFace format)
    "siglip_so400m_patch14_384": "/kaggle/input/google-siglip-so400m-patch14-384/transformers/default/1",
}


def get_pretrained_weights_path(model_name: str) -> str:
    """
    Get pretrained weights path/name from MODEL_NAME.

    Args:
        model_name: Model name (e.g., 'dinov2_base', 'timm_efficientnet_b3')

    Returns:
        Pretrained weights path (for DINOv2) or model name (for timm).
        Falls back to extracting timm name if model_name starts with 'timm_'.
        Falls back to model_name itself if no mapping found.
    """
    if model_name in _MODEL_NAME_TO_PRETRAINED:
        return _MODEL_NAME_TO_PRETRAINED[model_name]
    if model_name.startswith("timm_"):
        return model_name.replace("timm_", "")
    return model_name


def get_model_name_from_pretrained(pretrained_path: str) -> Optional[str]:
    """
    Reverse lookup: Get MODEL_NAME from pretrained weights path/name.
    """
    for model_name, pretrained in _MODEL_NAME_TO_PRETRAINED.items():
        if pretrained == pretrained_path:
            return model_name
    if not pretrained_path.startswith("/") and "/" not in pretrained_path:
        return f"timm_{pretrained_path}"
    return None

def get_model_image_size(model_name: str) -> Tuple[int, int]:
    """
    Get image size for a model without loading the model.

    Extracts image size from model name or uses defaults based on model type.
    This avoids loading the model just to get its input size.

    Args:
        model_name: Model name (e.g., 'dinov2_base', 'siglip_so400m_patch14_384', 'timm_efficientnet_b3')

    Returns:
        Tuple of (height, width) for the model's input size

    Raises:
        ValueError: If model name cannot be determined or size cannot be inferred
    """
    model_name_lower = (model_name or "").lower()

    # SigLIP models: Extract from name pattern (e.g., patch14_384 -> 384)
    if "siglip" in model_name_lower:
        # Try to extract size from model name (e.g., 'siglip_so400m_patch14_384' -> 384)
        import re
        match = re.search(r"patch\d+_(\d+)", model_name_lower)
        if match:
            size = int(match.group(1))
            return (size, size)
        # Default for SigLIP models if pattern not found
        return (384, 384)

    # DINOv2 models: Standard size is 518
    if "dinov2" in model_name_lower or "dinov3" in model_name_lower:
        return (518, 518)

    # Timm models: Default to 224, but could be overridden by specific model
    # For now, use default - could be enhanced to check specific timm model configs
    if "timm_" in model_name_lower or model_name in _MODEL_NAME_TO_PRETRAINED:
        # Check if it's a known timm model with specific size
        if "efficientnet_b3" in model_name_lower:
            return (300, 300)
        return (224, 224)

    # Fallback: default size
    return (224, 224)
