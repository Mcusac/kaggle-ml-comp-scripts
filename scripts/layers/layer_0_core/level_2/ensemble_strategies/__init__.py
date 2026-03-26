"""Ensemble strategy implementations.

This sub-package contains different strategies for combining predictions
from multiple base models:

- Averaging strategies: Simple, Weighted, Ranked, Percentile
- Target-specific: Use different models for different targets
- Per-target weighted: Different weights for each target

All strategies implement the EnsemblingMethod interface.
"""

from .averaging import (
    model_rank_weights,
    simple_average,
    weighted_average,
    value_rank_average,
    value_percentile_average,
    power_average,
    geometric_mean,
    max_ensemble,
    merge_submissions,
)
from .result_handler_common import _log_pipeline_completion
from .weight_matrix_builder import build_weight_matrix

__all__ = [
    'model_rank_weights',
    'simple_average',
    'weighted_average',
    'value_rank_average',    
    'value_percentile_average',
    'power_average',
    'geometric_mean',    
    'max_ensemble',
    'merge_submissions',
    '_log_pipeline_completion',
    'build_weight_matrix'
]