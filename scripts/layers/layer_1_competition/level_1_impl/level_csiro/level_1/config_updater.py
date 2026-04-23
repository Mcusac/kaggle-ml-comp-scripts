"""Config updater utilities."""

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import validate_config_section_exists

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import find_metadata_dir, load_combo_metadata

_logger = get_logger(__name__)


def apply_data_combo(config, combo: dict) -> None:
    validate_config_section_exists(config, "data")

    config.data.preprocessing_list = combo.get("preprocessing_list", [])
    config.data.augmentation_list = combo.get("augmentation_list", [])
    config.data.use_augmentation = bool(config.data.augmentation_list)


def _load_combo_metadata(metadata_dir: Path, combo_id: str) -> dict:
    metadata = load_combo_metadata(metadata_dir)
    
    combos = metadata.get('combos', {})
    if combo_id not in combos:
        raise ValueError(
            f"Combo '{combo_id}' not found in metadata. "
            f"Available combos: {list(combos.keys())[:10]}..."
        )
    
    return combos[combo_id]


def apply_combo_to_config(config: Any, combo_id: str) -> None:
    """
    Apply data manipulation combo to config by loading combo details from metadata.
    
    Loads preprocessing_list and augmentation_list for the given combo_id from
    metadata and applies them to config. This is contest-specific and requires
    metadata directory structure.
    
    Args:
        config: Contest config object (must have data section with preprocessing_list/augmentation_list)
        combo_id: Combo ID (e.g., 'combo_00', 'combo_63')
        
    Notes:
        - Contest-specific: Requires metadata directory structure
        - For vision contests: Applies preprocessing and augmentation lists
        - For tabular contests: May not be applicable
        - Adaptation: Uses contest abstraction to find metadata paths
    """
    if config is None:
        raise ValueError("config cannot be None")
    
    if not combo_id or not isinstance(combo_id, str):
        raise ValueError(f"combo_id must be a non-empty string, got {combo_id}")
    
    try:
        metadata_dir = find_metadata_dir()
        combo = _load_combo_metadata(metadata_dir, combo_id)
        apply_data_combo(config, combo)
        _logger.info(f"✓ Applied data manipulation combo '{combo_id}'")
    except (FileNotFoundError, ValueError) as e:
        raise
    except Exception as e:
        raise ValueError(f"Failed to load or apply combo '{combo_id}': {e}")
