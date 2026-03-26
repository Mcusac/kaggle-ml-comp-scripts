"""Variant result builders for hyperparameter and regression grid search."""

from typing import Dict, Any, Optional, List

from level_0 import create_result_dict, create_error_result_dict
from level_6 import create_variant_specific_data


def build_success_result(
    variant_index: int,
    variant_id: str,
    cv_score: Optional[float],
    fold_scores: Optional[List[float]],
    batch_size_used: Optional[int],
    batch_size_reduced: bool,
    config: Any,
    hyperparameters: Dict[str, Any],
    feature_filename: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a success variant result dict using shared helpers.
    """
    variant_specific_data = create_variant_specific_data(
        config=config,
        hyperparameters=hyperparameters,
        feature_filename=feature_filename,
    )
    result = create_result_dict(
        variant_index=variant_index,
        variant_id=variant_id,
        cv_score=cv_score,
        fold_scores=fold_scores,
        batch_size_used=batch_size_used if batch_size_used is not None else 0,
        batch_size_reduced=batch_size_reduced,
        variant_specific_data=variant_specific_data,
    )
    if extra_fields:
        result.update(extra_fields)
    return result


def build_error_result(
    variant_index: int,
    variant_id: str,
    error: str,
    batch_size_used: int,
    batch_size_reduced: bool,
    config: Any,
    hyperparameters: Dict[str, Any],
    skipped: bool = False,
) -> Dict[str, Any]:
    """
    Build an error variant result dict.
    """
    variant_specific_data = create_variant_specific_data(
        config=config,
        hyperparameters=hyperparameters,
    )
    return create_error_result_dict(
        variant_index=variant_index,
        variant_id=variant_id,
        error=error,
        batch_size_used=batch_size_used,
        batch_size_reduced=batch_size_reduced,
        variant_specific_data=variant_specific_data,
        skipped=skipped,
    )
