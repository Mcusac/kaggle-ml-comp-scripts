"""Metadata fallback utilities."""

from typing import Dict, Any, Optional

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def load_feature_filename_from_gridsearch(
    variant_id: str,
    regression_model_type: str,
    metadata: Dict[str, Any],
    contest_context: Any = None
) -> Optional[str]:
    """
    Load feature_filename from grid search metadata as fallback.

    Contest-agnostic: uses contest_context.load_regression_gridsearch_results if provided
    (contest layer injects this so orchestration does not import contest).

    Args:
        variant_id: Variant ID
        regression_model_type: Regression model type
        metadata: Current metadata dictionary (will be updated)
        contest_context: Optional context with load_regression_gridsearch_results(regression_model_type, variant_id=, feature_filename=)

    Returns:
        Feature filename if found, None otherwise
    """
    if not variant_id or not regression_model_type:
        _logger.warning(
            f"feature_filename not found in exported metadata and cannot fallback: "
            f"variant_id={variant_id}, regression_model_type={regression_model_type}. "
            f"Please ensure the exported model_metadata.json contains 'feature_filename'."
        )
        return None

    loader = getattr(contest_context, "load_regression_gridsearch_results", None) if contest_context else None
    if loader is None:
        return None

    _logger.info(f"feature_filename not in exported metadata, looking up from grid search metadata...")
    try:
        results = loader(
            regression_model_type=regression_model_type,
            variant_id=variant_id
        )
        if results:
            # Use the result with highest cv_score
            best_result = max(results, key=lambda x: x.get('cv_score', -float('inf')))
            feature_filename = best_result.get('feature_filename')
            if feature_filename:
                metadata['feature_filename'] = feature_filename
                _logger.info(
                    f"Found feature_filename from grid search metadata: {feature_filename} "
                    f"(cv_score: {best_result.get('cv_score', 0):.4f})"
                )
                return feature_filename
            else:
                _logger.warning(f"feature_filename not found in grid search result for variant {variant_id}")
        else:
            _logger.warning(f"No grid search results found for variant {variant_id}")
    except Exception as e:
        _logger.warning(
            f"Could not load feature_filename from grid search metadata: {e}. "
            f"Please ensure the exported model_metadata.json contains 'feature_filename'."
        )

    return None
