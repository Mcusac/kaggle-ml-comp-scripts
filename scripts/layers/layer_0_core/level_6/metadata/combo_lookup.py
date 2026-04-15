"""Lookup utilities for data-manipulation combo ids (depends on level_5 metadata paths)."""

from typing import Any, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json_raw
from layers.layer_0_core.level_5 import find_metadata_dir

logger = get_logger(__name__)


def find_combo_id_from_config(config: Any) -> Optional[str]:
    try:
        preprocessing_list = getattr(config.data, "preprocessing_list", []) or []
        augmentation_list = getattr(config.data, "augmentation_list", []) or []
        metadata_dir = find_metadata_dir()
        if not metadata_dir:
            return None
        combo_metadata_path = metadata_dir / "data_manipulation" / "metadata.json"
        if not combo_metadata_path.exists():
            return None
        combos_list = load_json_raw(combo_metadata_path)
        for combo in combos_list:
            if combo.get("preprocessing_list") == preprocessing_list and combo.get("augmentation_list") == augmentation_list:
                return combo.get("combo_id")
        return None
    except Exception as e:
        logger.warning(f"Could not find combo_id: {e}")
        return None

