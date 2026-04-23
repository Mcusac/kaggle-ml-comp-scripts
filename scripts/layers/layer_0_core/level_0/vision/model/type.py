"""Generic vision model type detection from model name or path."""

from typing import Callable, Optional


def detect_vision_model_type(
    model: str,
    *,
    dinov2_policy: Optional[Callable[[str], bool]] = None,
) -> str:
    """
    Detect vision model type from model name or path.

    Returns one of: 'dinov2_hf', 'siglip', 'timm'.

    Args:
        model: Model architecture name or HuggingFace/local path.
        dinov2_policy: Optional callable that returns True if DINOv2 is allowed
            for this path. If None, any DINOv2-like name returns 'dinov2_hf'.
            If provided and returns False, ValueError is raised (contest policy).

    Returns:
        Model type string for use with the model factory.

    Raises:
        ValueError: If dinov2_policy rejects the path (e.g. DINOv2 must be HF).
    """
    model_lower = model.lower()

    if "siglip" in model_lower:
        return "siglip"

    if "dinov2" in model_lower or "dinov3" in model_lower:
        if dinov2_policy is None or dinov2_policy(model):
            return "dinov2_hf"
        raise ValueError(
            "DINOv2 only supports HuggingFace format. "
            f"'{model}' does not appear to be a HuggingFace path or local directory. "
            "Use TimmModel for timm-format models."
        )

    return "timm"
