"""
Unified entry point for metric calculation.

Provides a simple interface for calculating metrics based on task type,
with support for both generic and contest-specific metrics.
"""

import numpy as np

from typing import Dict, Optional, Any, Union

from level_0 import get_logger
from level_1 import get_metric, list_metrics
from level_3 import (
    calculate_classification_metrics,
    calculate_regression_metrics,
)

logger = get_logger(__name__)


def calculate_metrics(
    task_type: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    contest: Optional[str] = None,
    **kwargs,
) -> Dict[str, float]:
    """
    Unified entry point for metric calculation.
    
    Automatically selects appropriate metrics based on task type
    and optional contest specification.
    
    Args:
        task_type: Type of task - "classification" or "regression".
        y_true: Ground truth values/labels.
        y_pred: Predicted values/labels.
        contest: Optional contest name for contest-specific metrics
                (e.g., "csiro", "cafa"). If None, uses generic metrics.
        **kwargs: Additional arguments passed to metric calculators:
                 - For classification: y_pred_proba, average, sample_weight
                 - For regression: target_names, sample_weight
                 - For contest-specific: weights, target_order, etc.
        
    Returns:
        Dictionary of metric name -> value.
        
    Raises:
        ValueError: If task_type is unknown or contest metric not found.
        
    Example:
        >>> # Generic classification
        >>> metrics = calculate_metrics(
        ...     "classification",
        ...     y_true=labels,
        ...     y_pred=predictions,
        ...     y_pred_proba=probabilities
        ... )
        
        >>> # Generic regression
        >>> metrics = calculate_metrics(
        ...     "regression",
        ...     y_true=targets,
        ...     y_pred=predictions,
        ...     target_names=["height", "weight"]
        ... )
        
        >>> # Contest-specific (CSIRO)
        >>> metrics = calculate_metrics(
        ...     "regression",
        ...     y_true=targets,
        ...     y_pred=predictions,
        ...     contest="csiro",
        ...     weights=csiro_weights
        ... )
    """
    task_type = task_type.lower()
    
    # Handle contest-specific metrics
    if contest:
        contest_metric = get_metric(f"{contest}_weighted_r2")
        if contest_metric is None:
            available = list_metrics()
            raise ValueError(
                f"Contest metric for '{contest}' not found. "
                f"Available metrics: {available}"
            )
        
        logger.info(f"Using contest-specific metric: {contest}")
        result = contest_metric.calculate(y_true, y_pred, **kwargs)
        
        # Ensure result is a dict
        if isinstance(result, dict):
            return result
        else:
            return {contest_metric.name: result}
    
    # Handle generic metrics by task type
    if task_type == "classification":
        return calculate_classification_metrics(y_true, y_pred, **kwargs)
    
    if task_type == "regression":
        return calculate_regression_metrics(y_true, y_pred, **kwargs)
    
    raise ValueError(
        f"Unsupported task_type: '{task_type}'. "
        f"Must be 'classification' or 'regression'"
    )


def calculate_metric_by_name(
    metric_name: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    **kwargs
) -> Union[float, Dict[str, Any]]:
    """
    Calculate a specific metric by name.
    
    Args:
        metric_name: Name of the metric to calculate (e.g., 'rmse', 'f1_macro').
        y_true: Ground truth values/labels.
        y_pred: Predicted values/labels.
        **kwargs: Additional arguments passed to the metric.
        
    Returns:
        Metric value (float) or dictionary of values.
        
    Raises:
        ValueError: If metric_name is not registered.
        
    Example:
        >>> rmse = calculate_metric_by_name("rmse", y_true, y_pred)
        >>> f1 = calculate_metric_by_name("f1_macro", y_true, y_pred)
        >>> csiro_results = calculate_metric_by_name(
        ...     "csiro_weighted_r2",
        ...     y_true,
        ...     y_pred,
        ...     weights=weights
        ... )
    """
    metric = get_metric(metric_name)
    
    if metric is None:
        available = list_metrics()
        raise ValueError(
            f"Metric '{metric_name}' not registered. "
            f"Available metrics: {available}"
        )
    
    return metric.calculate(y_true, y_pred, **kwargs)