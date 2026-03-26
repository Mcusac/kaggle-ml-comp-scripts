"""Results analysis: fold statistics and CV-test gap warnings."""

import statistics

from typing import List, Optional, Dict

from level_0 import get_logger

logger = get_logger(__name__)


def calculate_fold_statistics(fold_scores: List[float]) -> Dict[str, float]:
    """
    Calculate statistics for fold scores.

    Args:
        fold_scores: List of fold scores

    Returns:
        Dictionary with fold statistics
    """
    fold_mean = statistics.mean(fold_scores)
    fold_std = statistics.stdev(fold_scores) if len(fold_scores) > 1 else 0.0
    fold_min = min(fold_scores)
    fold_max = max(fold_scores)
    fold_range = fold_max - fold_min

    return {
        'fold_mean': fold_mean,
        'fold_std': fold_std,
        'fold_min': fold_min,
        'fold_max': fold_max,
        'fold_range': fold_range
    }


def generate_cv_test_gap_warnings(
    cv_score: float,
    fold_mean: float,
    fold_range: float,
    test_score: Optional[float],
    threshold: float
) -> List[str]:
    """
    Generate warning messages for CV-test gap analysis.

    Args:
        cv_score: Average CV score
        fold_mean: Mean of fold scores
        fold_range: Range of fold scores
        test_score: Optional test score
        threshold: Gap threshold

    Returns:
        List of warning messages
    """
    warnings = []

    # Check for large range (high variance indicator)
    if fold_range > 0.2:
        warnings.append(
            f"⚠️ Large fold score range detected ({fold_range:.4f}). "
            f"This suggests high variance in model performance across folds."
        )

    # Check if CV score matches fold mean (should be close)
    if abs(cv_score - fold_mean) > 1e-6:
        warnings.append(
            f"⚠️ CV score ({cv_score:.6f}) doesn't match fold mean ({fold_mean:.6f}). "
            f"This may indicate an error in score calculation."
        )

    # Analyze CV vs test gap if test score provided
    if test_score is not None:
        cv_test_gap = cv_score - test_score

        if cv_test_gap > threshold:
            warnings.append(
                f"⚠️ Large CV-test gap detected ({cv_test_gap:.4f}, threshold: {threshold}). "
                f"CV score ({cv_score:.4f}) is much higher than test score ({test_score:.4f}). "
                f"This may indicate overfitting. Possible causes: overfitting to validation folds, "
                f"distribution shift, or model instability."
            )
            logger.warning(
                f"⚠️ Large CV-test gap detected: {cv_test_gap:.4f} (threshold: {threshold}). "
                f"This may indicate overfitting. CV: {cv_score:.4f}, Test: {test_score:.4f}"
            )
        elif cv_test_gap < -0.1:  # Test is much better (unusual)
            warnings.append(
                f"⚠️ Test score ({test_score:.4f}) is much higher than CV score ({cv_score:.4f}). "
                f"This is unusual and may indicate issues with validation set or test set leakage."
            )

    return warnings
