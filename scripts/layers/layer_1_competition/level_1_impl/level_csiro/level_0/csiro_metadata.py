"""CSIRO metadata helpers for variant and combo resolution."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_5 import (
    find_metadata_dir as _find_metadata_dir_raw,
    get_writable_metadata_dir as _get_writable_metadata_dir_raw,
    load_combo_metadata as _load_combo_raw,
)

CSIRO_DATASET_NAME = "csiro-metadata"
CSIRO_COMBO_SUBPATH = "data_manipulation/metadata.json"


def find_metadata_dir() -> Optional[Path]:
    """Find the csiro-metadata directory for reading."""
    return _find_metadata_dir_raw(CSIRO_DATASET_NAME)


def get_writable_metadata_dir() -> Path:
    """Get the writable csiro-metadata directory. Creates it if missing."""
    return _get_writable_metadata_dir_raw(CSIRO_DATASET_NAME)


def load_combo_metadata(metadata_dir: Path) -> dict:
    """Load CSIRO combo metadata from metadata_dir."""
    return _load_combo_raw(metadata_dir, CSIRO_COMBO_SUBPATH)


_logger = get_logger(__name__)


def _get_combo_details(combo_id: str, metadata_dir: Path) -> Dict[str, List[str]]:
    """Load combo details from metadata. Handles list or combos-dict format."""
    raw = _load_combo_raw(metadata_dir, CSIRO_COMBO_SUBPATH)

    if isinstance(raw, list):
        for combo in raw:
            if combo.get("combo_id") == combo_id:
                return {
                    "preprocessing_list": combo.get("preprocessing_list", []),
                    "augmentation_list": combo.get("augmentation_list", []),
                }
        available = ", ".join(
            str(c.get("combo_id", "?")) for c in raw[:10]
        )
        raise ValueError(
            f"Combo ID '{combo_id}' not found in metadata. "
            f"Available (first 10): {available}..."
        )

    combos = raw.get("combos", {})
    if combo_id not in combos:
        available = ", ".join(sorted(combos.keys())[:10])
        raise ValueError(
            f"Combo ID '{combo_id}' not found in metadata. "
            f"Available (first 10): {available}..."
        )

    combo = combos[combo_id]
    return {
        "preprocessing_list": combo.get("preprocessing_list", []),
        "augmentation_list": combo.get("augmentation_list", []),
    }


def extract_preprocessing_augmentation_from_variant(
    variant: Dict[str, Any],
    metadata_dir: Optional[Path] = None
) -> Tuple[List[str], List[str]]:
    """Extract preprocessing_list and augmentation_list from a variant result.

    Resolves data_manipulation.combo_id via metadata. Does not support
    legacy format with direct preprocessing_list/augmentation_list keys.

    Args:
        variant: Variant dictionary from results.
        metadata_dir: Optional metadata directory. If None, uses find_metadata_dir().

    Returns:
        Tuple of (preprocessing_list, augmentation_list).

    Raises:
        ValueError: If variant has data_manipulation but combo_id cannot be resolved.
    """
    data_manipulation = variant.get("data_manipulation")

    if not data_manipulation:
        raise ValueError(
            f"Variant {variant.get('variant_id', 'unknown')} missing data_manipulation. "
            "All variants must use data_manipulation.combo_id format."
        )

    combo_id = data_manipulation.get("combo_id")
    if not combo_id:
        raise ValueError(
            f"Variant {variant.get('variant_id', 'unknown')} has data_manipulation "
            "but no combo_id"
        )

    if metadata_dir is None:
        metadata_dir = find_metadata_dir()

    if not metadata_dir or not metadata_dir.exists():
        raise FileNotFoundError(
            "Cannot resolve combo_id: metadata directory not found. "
            "Expected: /kaggle/input/csiro-metadata (Kaggle) or ../csiro-metadata (local)"
        )

    details = _get_combo_details(combo_id, metadata_dir)
    return details["preprocessing_list"], details["augmentation_list"]
