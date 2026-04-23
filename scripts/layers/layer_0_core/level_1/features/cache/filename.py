"""Codec for feature cache filenames: encode (model_id, combo_id) → filename and back."""

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def generate_feature_filename(model_id: str, combo_id: str = "combo_00") -> str:
    """Encode (model_id, combo_id) into a canonical feature cache filename.

    Args:
        model_id: Two-character model identifier string.
        combo_id: Combo identifier in the format 'combo_XX'. Defaults to 'combo_00'.

    Returns:
        Filename string, e.g. 'variant_0100_features.npz'.

    Raises:
        ValueError: If combo_id format is invalid.
    """
    if not combo_id.startswith("combo_"):
        raise ValueError(f"Invalid combo_id format: {combo_id!r}. Expected format: combo_XX")
    try:
        combo_numeric = combo_id.replace("combo_", "")
        combo_numeric_2digit = f"{int(combo_numeric):02d}"
    except ValueError:
        raise ValueError(f"Invalid combo_id numeric part: {combo_id!r}")
    filename = f"variant_{model_id}{combo_numeric_2digit}_features.npz"
    _logger.debug(f"Generated feature filename: {filename} (model_id={model_id}, combo_id={combo_id})")
    return filename


def parse_feature_filename(filename: str) -> tuple[str, str]:
    """Decode a canonical feature cache filename into (model_id, combo_id).

    Args:
        filename: Filename string, e.g. 'variant_0100_features.npz'.

    Returns:
        Tuple of (model_id, combo_id).

    Raises:
        ValueError: If filename does not match the expected format.
    """
    if not filename.startswith("variant_"):
        raise ValueError(
            f"Invalid feature filename: {filename!r}. Expected format: variant_XXXX_features.npz"
        )
    if not filename.endswith("_features.npz"):
        raise ValueError(
            f"Invalid feature filename: {filename!r}. Expected format: variant_XXXX_features.npz"
        )
    middle_part = filename.replace("variant_", "").replace("_features.npz", "")
    if len(middle_part) != 4:
        raise ValueError(
            f"Invalid feature filename: {filename!r}. Expected exactly 4 characters between 'variant_' and '_features.npz'"
        )
    model_id = middle_part[:2]
    combo_id = f"combo_{middle_part[2:]}"
    return model_id, combo_id