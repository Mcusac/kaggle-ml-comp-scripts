"""Export operations for train-and-export pipeline."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_5 import export_from_training_dir

from layers.layer_1_competition.level_0_infra.level_1 import get_output_path

logger = get_logger(__name__)


def handle_export_only_mode(
    model: Optional[str],
    export_dir: Optional[str],
    regression_model_type: Optional[str],
    feature_extraction_model: Optional[str],
    data_manipulation_combo: Optional[str],
    dataset_type: str,
) -> None:
    """Handle export-only mode (no training)."""
    logger.info("Export mode: Reusing existing model (export_only=True)")

    if model is None:
        training_model_dir = Path(get_output_path("best_model_training"))
    else:
        training_model_dir = Path(get_output_path(f"{model}_training"))

    if not training_model_dir.exists():
        raise FileNotFoundError(f"Training directory not found: {training_model_dir}")

    export_metadata = {
        "model_name": model or "unknown",
        "regression_model_type": regression_model_type,
        "feature_extraction_model": feature_extraction_model,
        "data_manipulation_combo": data_manipulation_combo,
        "dataset_type": dataset_type,
    }

    metadata_file = training_model_dir / "model_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            existing_metadata = json.load(f)
            export_metadata.update(existing_metadata)

    export_dir_path = Path(export_dir) if export_dir else Path(get_output_path("exports"))
    export_dir_path.mkdir(parents=True, exist_ok=True)

    export_from_training_dir(
        model_dir=training_model_dir,
        export_dir=export_dir_path,
        metadata=export_metadata,
    )

    logger.info("Export complete!")


def export_trained_model(
    training_model_dir: Path,
    export_dir: str,
    regression_model_type: Optional[str],
    export_variant_info: Dict[str, Any],
    regression_variant_info: Optional[Dict[str, Any]],
    regression_model_variant_id: Optional[str],
) -> None:
    """Export trained model to export directory."""
    logger.info("Exporting trained model...")
    export_dir_path = Path(export_dir)
    export_dir_path.mkdir(parents=True, exist_ok=True)

    variant_id = export_variant_info.get("variant_id")
    variant_index = export_variant_info.get("variant_index", 0)
    if regression_variant_info:
        variant_id = regression_variant_info.get("variant_id")
        variant_index = regression_variant_info.get("variant_index", 0)

    export_metadata = {
        "regression_model_type": regression_model_type,
        "variant_id": variant_id,
        "variant_index": variant_index,
        "feature_filename": export_variant_info.get("feature_filename"),
        "cv_score": export_variant_info.get("cv_score"),
        "fold_scores": export_variant_info.get("fold_scores", []),
        "best_fold": export_variant_info.get("best_fold"),
        "best_fold_score": export_variant_info.get("best_fold_score"),
        "hyperparameters": export_variant_info.get("hyperparameters", {}),
    }

    export_from_training_dir(
        model_dir=training_model_dir,
        export_dir=export_dir_path,
        metadata=export_metadata,
    )

    logger.info("=" * 60)
    logger.info("Model trained and exported successfully!")
    if regression_variant_info:
        logger.info("   Regression Variant ID: %s", regression_variant_info.get("variant_id"))
        if regression_model_variant_id:
            logger.info("   Selection: Manually specified variant")
        else:
            logger.info("   Selection: Best variant (highest CV score)")
        cv_score = export_variant_info.get("cv_score")
        if cv_score is not None:
            logger.info("   CV Score: %.4f", cv_score)
        else:
            logger.info("   CV Score: N/A (variant not yet trained for this feature file)")
    logger.info("=" * 60)
