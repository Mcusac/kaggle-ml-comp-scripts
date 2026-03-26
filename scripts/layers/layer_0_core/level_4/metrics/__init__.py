"""Unified metric calculation entry points for classification and regression tasks."""

from .calculate_metrics import calculate_metrics, calculate_metric_by_name
from .weighted_r2 import create_weighted_r2_calculator

__all__ = [
    "calculate_metrics",
    "calculate_metric_by_name",
    "create_weighted_r2_calculator"
]