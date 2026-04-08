"""Feature-filename construction helpers for export metadata."""

from typing import Any, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import generate_feature_filename, get_model_id

from layers.layer_1_competition.level_0_infra.level_0 import get_model_name_from_pretrained
from layers.layer_0_core.level_6 import find_combo_id_from_config

logger = get_logger(__name__)


def resolve_feature_extraction_model_name(config: Any) -> Optional[str]:
    feature_extraction_model_name = getattr(config.model, "feature_extraction_model_name", None)
    if not feature_extraction_model_name:
        return None
    if "/" in feature_extraction_model_name or feature_extraction_model_name.startswith("/"):
        resolved_name = get_model_name_from_pretrained(feature_extraction_model_name)
        if resolved_name:
            return resolved_name
    return feature_extraction_model_name


def construct_feature_filename_from_config(config: Any) -> Optional[str]:
    """Construct feature filename from feature-extraction config settings."""
    if not getattr(config.model, "feature_extraction_mode", False):
        return None
    try:
        model_name = resolve_feature_extraction_model_name(config)
        if not model_name:
            return None
        combo_id = find_combo_id_from_config(config)
        if not combo_id:
            return None
        model_id = get_model_id(model_name)
        feature_filename = generate_feature_filename(model_id, combo_id)
        logger.info(f"Constructed feature_filename from config: {feature_filename}")
        return feature_filename
    except Exception as e:
        logger.warning(f"Could not construct feature_filename from config: {e}")
        return None

