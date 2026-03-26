"""Fold score analysis utilities for cross-validation results."""

import math

from typing import List, Tuple, Dict, Any, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import calculate_fold_statistics, generate_cv_test_gap_warnings

logger = get_logger(__name__)


def find_best_fold_from_scores(fold_scores: List[float]) -> Tuple[int, float]:
    """
    Find the best fold from a list of fold scores.

    Args:
        fold_scores: List of scores for each fold. Must not be empty.
                     Each element must be numeric. Higher scores are better.

    Returns:
        Tuple of (best_fold_index, best_score).

    Raises:
        TypeError: If fold_scores is not a list.
        ValueError: If fold_scores is empty, contains non-numeric values,
                    or the best score is NaN.
    """
    if not isinstance(fold_scores, list):
        raise TypeError(f"fold_scores must be a list, got {type(fold_scores)}")

    if not fold_scores:
        raise ValueError("fold_scores cannot be empty")

    for i, score in enumerate(fold_scores):
        if not isinstance(score, (int, float)):
            raise ValueError(
                f"fold_scores[{i}] must be numeric (int or float), got {type(score)}"
            )

    best_fold = max(range(len(fold_scores)), key=lambda i: fold_scores[i])
    best_score = fold_scores[best_fold]

    if math.isnan(best_score):
        raise ValueError("All fold scores are NaN or best score is NaN")

    return best_fold, best_score


def analyze_cv_test_gap(
    cv_score: float,
    fold_scores: List[float],
    test_score: Optional[float] = None,
    threshold: float = 0.15,
) -> Dict[str, Any]:
    """
    Analyze the gap between CV scores and test performance.

    Identifies potential issues such as overfitting to validation folds,
    high variance across folds, and distribution shift between train/val and test.

    Args:
        cv_score: Average cross-validation score.
        fold_scores: List of per-fold scores.
        test_score: Optional test score for comparison.
        threshold: Gap threshold for warning (default: 0.15).

    Returns:
        Dict with keys: cv_score, fold_scores, fold_mean, fold_std, fold_range,
        fold_min, fold_max, test_score, cv_test_gap, warnings, warn.

    Raises:
        ValueError: If fold_scores is empty or has fewer than 2 entries.
    """
    if not fold_scores:
        raise ValueError("fold_scores cannot be empty")

    if len(fold_scores) < 2:
        raise ValueError("Need at least 2 fold scores for analysis")

    stats = calculate_fold_statistics(fold_scores)
    fold_mean = stats['fold_mean']
    fold_std = stats['fold_std']
    fold_min = stats['fold_min']
    fold_max = stats['fold_max']
    fold_range = stats['fold_range']

    warnings = generate_cv_test_gap_warnings(
        cv_score, fold_mean, fold_range, test_score, threshold
    )

    cv_test_gap = (cv_score - test_score) if test_score is not None else None

    return {
        'cv_score': cv_score,
        'fold_scores': fold_scores,
        'fold_mean': fold_mean,
        'fold_std': fold_std,
        'fold_range': fold_range,
        'fold_min': fold_min,
        'fold_max': fold_max,
        'test_score': test_score,
        'cv_test_gap': cv_test_gap,
        'warnings': warnings,
        'warn': len(warnings) > 0,
    }


def analyze_fold_score_range(
    fold_scores: List[float],
    threshold: float = 0.2,
) -> Dict[str, Any]:
    """
    Analyze fold score range to detect high variance.

    Args:
        fold_scores: List of per-fold scores.
        threshold: Range threshold above which a warning is logged (default: 0.2).

    Returns:
        Dict with keys: fold_scores, fold_range, min_score, max_score, warn.
    """
    if not fold_scores:
        return {
            'fold_scores': [],
            'fold_range': 0.0,
            'min_score': None,
            'max_score': None,
            'warn': False,
        }

    fold_range = max(fold_scores) - min(fold_scores)
    if fold_range > threshold:
        logger.warning(
            f"Large fold score range detected: {fold_range:.4f} (threshold: {threshold}). "
            f"High variance across folds may indicate model instability. "
            f"Scores: {fold_scores}"
        )

    return {
        'fold_scores': fold_scores,
        'fold_range': fold_range,
        'min_score': min(fold_scores),
        'max_score': max(fold_scores),
        'warn': fold_range > threshold,
    }