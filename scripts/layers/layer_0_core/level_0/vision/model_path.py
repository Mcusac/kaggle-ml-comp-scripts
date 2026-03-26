"""HuggingFace model path detection utilities.

Provides the general-purpose path heuristic only.
Model-family-specific detection (siglip, dinov2, timm) belongs in the
contest/application layer (``layer_1_competition``) which imports this primitive.
"""

from pathlib import Path


def is_huggingface_model_path(model: str) -> bool:
    """
    Return True if model string looks like a HuggingFace path or local directory.

    A model string is treated as a HuggingFace reference if:
      - It contains '/'  (e.g. 'google/vit-base-patch16-224',
                               'facebook/dinov2-base')
      - It is an existing local directory (a downloaded HF model snapshot)

    Strings without '/' that do not resolve to a directory are treated as
    timm-style architecture names (e.g. 'resnet50', 'efficientnet_b0').

    Args:
        model: Model name or path string.

    Returns:
        True if the string appears to be a HuggingFace model reference.

    Examples:
        >>> is_huggingface_model_path("google/siglip-base-patch16-224")
        True
        >>> is_huggingface_model_path("/checkpoints/dinov2_snapshot")  # local dir
        True
        >>> is_huggingface_model_path("resnet50")
        False
    """
    return "/" in model or (Path(model).exists() and Path(model).is_dir())