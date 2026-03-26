"""Standard result dict builders for grid search variants."""

from typing import Dict, Any, Optional, List


def create_result_dict(
    variant_index: int,
    variant_id: str,
    cv_score: Optional[float],
    fold_scores: Optional[List[float]],
    batch_size_used: int,
    batch_size_reduced: bool,
    variant_specific_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a success variant result dict.

    Args:
        variant_index: Zero-based index of the variant.
        variant_id: Unique identifier for the variant.
        cv_score: Cross-validation score (None if not computed).
        fold_scores: Per-fold scores (None if not computed).
        batch_size_used: Batch size used for training.
        batch_size_reduced: Whether batch size was reduced due to OOM.
        variant_specific_data: Variant-specific metadata (preprocessing, hyperparams, etc.).

    Returns:
        Standardized result dictionary.
    """
    return {
        "variant_index": variant_index,
        "variant_id": variant_id,
        "cv_score": cv_score,
        "fold_scores": fold_scores,
        "batch_size_used": batch_size_used,
        "batch_size_reduced": batch_size_reduced,
        "variant_specific_data": variant_specific_data,
        "success": True,
    }


def create_error_result_dict(
    variant_index: int,
    variant_id: str,
    error: str,
    batch_size_used: Optional[int],
    batch_size_reduced: bool,
    variant_specific_data: Dict[str, Any],
    skipped: bool = False,
) -> Dict[str, Any]:
    """
    Build an error variant result dict.

    Args:
        variant_index: Zero-based index of the variant.
        variant_id: Unique identifier for the variant.
        error: Error message.
        batch_size_used: Batch size used (0 if not applicable).
        batch_size_reduced: Whether batch size was reduced.
        variant_specific_data: Variant-specific metadata.
        skipped: Whether the variant was skipped (e.g. already completed).

    Returns:
        Standardized error result dictionary.
    """
    return {
        "variant_index": variant_index,
        "variant_id": variant_id,
        "error": error,
        "batch_size_used": batch_size_used if batch_size_used is not None else 0,
        "batch_size_reduced": batch_size_reduced,
        "variant_specific_data": variant_specific_data,
        "skipped": skipped,
        "success": False,
    }
