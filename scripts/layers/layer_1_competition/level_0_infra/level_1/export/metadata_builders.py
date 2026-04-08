"""Metadata builder helpers used by model export flows."""

from pathlib import Path
from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import ConfigValidationError, get_logger
from layers.layer_1_competition.level_0_infra.level_1.export.feature_filename import (
    construct_feature_filename_from_config,
)
from layers.layer_0_core.level_5 import extract_scores_from_json, resolve_best_fold_and_score

logger = get_logger(__name__)


def prepare_regression_model_metadata_dict(
    regression_model_type: str,
    cv_score: float,
    fold_scores: list[float],
    hyperparameters: Dict[str, Any],
    feature_filename: str,
    variant_id: str,
    variant_index: int,
    best_fold: Optional[int] = None,
    best_fold_score: Optional[float] = None,
) -> Dict[str, Any]:
    """Create regression model metadata dictionary from explicit parameters."""
    metadata = {
        "regression_model_type": regression_model_type,
        "variant_index": variant_index,
        "variant_id": variant_id,
        "cv_score": cv_score,
        "fold_scores": fold_scores,
        "hyperparameters": hyperparameters,
        "feature_filename": feature_filename,
    }
    if best_fold is not None:
        metadata["best_fold"] = best_fold
    if best_fold_score is not None:
        metadata["best_fold_score"] = best_fold_score
    return metadata


def build_regression_metadata(
    config: Any,
    model_path: Path,
    best_fold: Optional[int],
    variant_id: Optional[str],
    variant_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build regression-model metadata for export manifests."""
    regression_model_type = getattr(config.model, "regression_model_type", None)
    if not regression_model_type:
        raise ConfigValidationError("regression_model_type must be set in config for regression model export")
    cv_score, fold_scores, extracted_best_fold = extract_scores_from_json(
        model_path=model_path,
        json_filename="regression_model_info.json",
        best_fold=best_fold,
    )
    best_fold_used, best_fold_score = resolve_best_fold_and_score(
        best_fold=best_fold,
        extracted_best_fold=extracted_best_fold,
        fold_scores=fold_scores,
        cv_score=cv_score,
    )
    feature_filename = variant_info.get("feature_filename") if variant_info else None
    if not feature_filename:
        feature_filename = construct_feature_filename_from_config(config)
    if not feature_filename:
        raise ValueError(
            "feature_filename is required for regression model export. "
            "Provide it in variant_info or ensure config has feature_extraction_model_name and data manipulation settings."
        )
    hyperparameters = variant_info.get("hyperparameters", {}) if variant_info else {}
    variant_id_used = variant_id or (variant_info.get("variant_id") if variant_info else None)
    variant_index_used = variant_info.get("variant_index") if variant_info else 0
    if not variant_id_used:
        raise ValueError("variant_id is required for regression model export. Provide it in variant_info or as parameter.")
    metadata = prepare_regression_model_metadata_dict(
        regression_model_type=regression_model_type,
        cv_score=cv_score,
        fold_scores=fold_scores,
        hyperparameters=hyperparameters,
        feature_filename=feature_filename,
        variant_id=variant_id_used,
        variant_index=variant_index_used,
        best_fold=best_fold_used,
        best_fold_score=best_fold_score,
    )
    logger.info(
        f"Built regression model metadata: regression_model_type={regression_model_type}, "
        f"feature_filename={feature_filename}"
    )
    return metadata


def build_end_to_end_metadata(
    config: Any,
    model_path: Path,
    best_fold: Optional[int],
    variant_id: Optional[str],
    variant_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build end-to-end model metadata for export manifests."""
    model_name = getattr(config.model, "name", "unknown")
    preprocessing_list = getattr(config.data, "preprocessing_list", []) or []
    augmentation_list = getattr(config.data, "augmentation_list", []) or []
    cv_score, fold_scores, extracted_best_fold = extract_scores_from_json(
        model_path=model_path,
        json_filename="checkpoint_metadata.json",
        best_fold=best_fold,
    )
    best_fold_used, best_fold_score = resolve_best_fold_and_score(
        best_fold=best_fold,
        extracted_best_fold=extracted_best_fold,
        fold_scores=fold_scores,
        cv_score=cv_score,
    )
    metadata = {
        "model_name": model_name,
        "preprocessing_list": preprocessing_list,
        "augmentation_list": augmentation_list,
        "cv_score": cv_score,
        "fold_scores": fold_scores,
        "best_fold": best_fold_used,
        "best_fold_score": best_fold_score,
        "dataset_type": getattr(config.data, "dataset_type", "split"),
    }
    if variant_id:
        metadata["variant_id"] = variant_id
    if variant_info:
        for key in ["variant_index", "feature_filename"]:
            if key in variant_info:
                metadata[key] = variant_info[key]
    return metadata

