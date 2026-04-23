"""Result persistence for train-and-export pipeline."""

from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_csiro.level_3.variant_selection_variants import (
    save_regression_gridsearch_result,
)

_logger = get_logger(__name__)


def save_regression_training_result(
    regression_model_type: str,
    export_variant_info: Dict[str, Any],
    regression_model_hyperparameters: Optional[Dict[str, Any]],
) -> None:
    """Save training result to gridsearch_metadata.json."""
    if not (
        regression_model_type
        and export_variant_info.get("variant_id")
        and export_variant_info.get("feature_filename")
    ):
        return

    try:
        save_regression_gridsearch_result(
            regression_model_type=regression_model_type,
            variant_id=export_variant_info.get("variant_id"),
            feature_filename=export_variant_info.get("feature_filename"),
            cv_score=export_variant_info.get("cv_score"),
            fold_scores=export_variant_info.get("fold_scores", []),
            hyperparameters=(
                export_variant_info.get("hyperparameters")
                or regression_model_hyperparameters
                or {}
            ),
        )
        _logger.info("Saved training result to gridsearch_metadata.json")
    except Exception as e:
        _logger.warning(
            "Failed to save training result to gridsearch_metadata.json: %s. "
            "Training completed successfully, but metadata was not updated.",
            e,
        )
