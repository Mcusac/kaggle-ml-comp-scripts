"""Contest-specific vision model type detection.

Thin wrapper around level_0.detect_vision_model_type with DINOv2-HF-only policy.
"""

from layers.layer_0_core.level_0 import detect_vision_model_type as _detect_vision_model_type, is_huggingface_model_path


def detect_model_type(model: str) -> str:
    """
    Detect vision model type from model name or path.

    Returns one of: 'dinov2_hf', 'siglip', 'timm'.

    Contest constraint: DINOv2 must be loaded from a HuggingFace path.
    """
    return _detect_vision_model_type(
        model,
        dinov2_policy=is_huggingface_model_path,
    )
