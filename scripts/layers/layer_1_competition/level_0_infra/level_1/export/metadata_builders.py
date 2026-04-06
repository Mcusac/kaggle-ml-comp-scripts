"""Metadata builder helpers used by model export flows."""

from __future__ import annotations

import json

from pathlib import Path
from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import ConfigValidationError, get_logger
from layers.layer_0_core.level_1 import generate_feature_filename
from layers.layer_0_core.level_5 import find_metadata_dir

from layers.layer_1_competition.level_0_infra.level_0 import get_model_id, get_model_name_from_pretrained

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


def _extract_scores_from_json(
    model_path: Path,
    json_filename: str,
    best_fold: Optional[int],
) -> tuple[float, list, Optional[int]]:
    """Extract CV/fold scores from a model-adjacent metadata JSON file."""
    metadata_path = model_path.parent / json_filename
    cv_score = 0.0
    fold_scores = []
    extracted_best_fold = best_fold
    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                info = json.load(f)
            cv_score = info.get("cv_score", 0.0)
            fold_scores = info.get("fold_scores", [])
            extracted_best_fold = info.get("best_fold", best_fold)
        except Exception as e:
            logger.warning(f"Could not load {json_filename}: {e}")
    return cv_score, fold_scores, extracted_best_fold


def _resolve_best_fold_and_score(
    best_fold: Optional[int],
    extracted_best_fold: Optional[int],
    fold_scores: list,
    cv_score: float,
) -> tuple[Optional[int], float]:
    """Resolve best fold index and score from fold data with cv fallback."""
    best_fold_used = best_fold if best_fold is not None else extracted_best_fold
    best_fold_score = (
        fold_scores[best_fold_used] if best_fold_used is not None and best_fold_used < len(fold_scores) else cv_score
    )
    return best_fold_used, best_fold_score


def _construct_feature_filename_from_config(config: Any) -> Optional[str]:
    """Construct feature filename from feature-extraction config settings."""
    if not getattr(config.model, "feature_extraction_mode", False):
        return None
    try:
        model_name = _resolve_feature_extraction_model_name(config)
        if not model_name:
            return None
        combo_id = _find_combo_id_from_config(config)
        if not combo_id:
            return None
        model_id = get_model_id(model_name)
        feature_filename = generate_feature_filename(model_id, combo_id)
        logger.info(f"Constructed feature_filename from config: {feature_filename}")
        return feature_filename
    except Exception as e:
        logger.warning(f"Could not construct feature_filename from config: {e}")
        return None


def _resolve_feature_extraction_model_name(config: Any) -> Optional[str]:
    feature_extraction_model_name = getattr(config.model, "feature_extraction_model_name", None)
    if not feature_extraction_model_name:
        return None
    if "/" in feature_extraction_model_name or feature_extraction_model_name.startswith("/"):
        resolved_name = get_model_name_from_pretrained(feature_extraction_model_name)
        if resolved_name:
            return resolved_name
    return feature_extraction_model_name


def _find_combo_id_from_config(config: Any) -> Optional[str]:
    try:
        preprocessing_list = getattr(config.data, "preprocessing_list", []) or []
        augmentation_list = getattr(config.data, "augmentation_list", []) or []
        metadata_dir = find_metadata_dir()
        if not metadata_dir:
            return None
        combo_metadata_path = metadata_dir / "data_manipulation" / "metadata.json"
        if not combo_metadata_path.exists():
            return None
        with open(combo_metadata_path, "r") as f:
            combos_list = json.load(f)
        for combo in combos_list:
            if combo.get("preprocessing_list") == preprocessing_list and combo.get("augmentation_list") == augmentation_list:
                return combo.get("combo_id")
        return None
    except Exception as e:
        logger.warning(f"Could not find combo_id: {e}")
        return None


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
    cv_score, fold_scores, extracted_best_fold = _extract_scores_from_json(model_path, "regression_model_info.json", best_fold)
    best_fold_used, best_fold_score = _resolve_best_fold_and_score(best_fold, extracted_best_fold, fold_scores, cv_score)
    feature_filename = variant_info.get("feature_filename") if variant_info else None
    if not feature_filename:
        feature_filename = _construct_feature_filename_from_config(config)
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
    cv_score, fold_scores, extracted_best_fold = _extract_scores_from_json(model_path, "checkpoint_metadata.json", best_fold)
    best_fold_used, best_fold_score = _resolve_best_fold_and_score(best_fold, extracted_best_fold, fold_scores, cv_score)
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

