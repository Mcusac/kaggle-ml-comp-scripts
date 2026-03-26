"""Model and feature filename resolution for train-and-export pipeline."""

from typing import Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import generate_feature_filename

from layers.layer_1_competition.level_0_infra.level_0 import get_model_id, get_model_name_from_pretrained, get_model_image_size

logger = get_logger(__name__)


def get_model_id_from_name(model_name: str) -> str:
    """
    Get two-digit model ID from model name.

    Handles both model names and pretrained paths.
    """
    if "/" in model_name or model_name.startswith("/"):
        resolved_name = get_model_name_from_pretrained(model_name)
        if resolved_name:
            model_name = resolved_name
        else:
            logger.warning(
                "Could not resolve model name from path '%s', using default model_id '01'",
                model_name,
            )
            return "01"

    try:
        return get_model_id(model_name)
    except ValueError as e:
        logger.warning("Could not get model_id for '%s': %s. Using default '01'", model_name, e)
        return "01"


def resolve_feature_filename(
    feature_extraction_model: Optional[str],
    data_manipulation_combo: Optional[str],
) -> Optional[str]:
    """
    Resolve feature filename from feature extraction model and data manipulation combo.
    """
    if not feature_extraction_model:
        return None

    combo_id = data_manipulation_combo or "combo_00"
    model_id = get_model_id_from_name(feature_extraction_model)

    try:
        feature_filename = generate_feature_filename(model_id, combo_id)
        logger.info(
            "Resolved feature filename: %s (model=%s, combo=%s)",
            feature_filename,
            feature_extraction_model,
            combo_id,
        )
        return feature_filename
    except ValueError as e:
        logger.warning("Could not generate feature filename: %s", e)
        return None


def get_model_image_size_for_extraction(feature_extraction_model: str) -> int:
    """Get image size for feature extraction model."""
    size_tuple = get_model_image_size(feature_extraction_model)
    image_size = size_tuple[0] if isinstance(size_tuple, (tuple, list)) else size_tuple
    if isinstance(image_size, tuple):
        image_size = image_size[0]
    logger.info("Using image size for model %s: %s", feature_extraction_model, image_size)
    return image_size
