"""Contest-specific vision model type detection.

Thin wrapper around core vision model type detection when available.
"""

try:
    from layers.layer_0_core.level_0 import is_huggingface_model_path
except ImportError:
    def is_huggingface_model_path(model: str) -> bool:  # type: ignore[no-redef]
        # Lightweight fallback: treat 'org/name' or 'hf://...' as HF-like.
        m = str(model or "").strip()
        return m.startswith("hf://") or ("/" in m and not m.startswith((".", "/", "\\")))
try:
    from layers.layer_0_core.level_0 import detect_vision_model_type as _detect_vision_model_type
except ImportError:
    _detect_vision_model_type = None  # type: ignore[assignment]


def detect_model_type(model: str) -> str:
    """
    Detect vision model type from model name or path.

    Returns one of: 'dinov2_hf', 'siglip', 'timm'.

    Contest constraint: DINOv2 must be loaded from a HuggingFace path.
    """
    if _detect_vision_model_type is None:
        raise RuntimeError(
            "Vision model type detection is unavailable (missing optional vision dependencies)."
        )
    return _detect_vision_model_type(
        model,
        dinov2_policy=is_huggingface_model_path,
    )
