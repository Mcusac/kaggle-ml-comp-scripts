"""Generic submission scaffolding (infra-level).

This package provides reusable helpers for assembling and saving submissions.
Contest-specific formatting stays in contest packages.
"""

from .csv_pipeline import expand_predictions_to_submission_format, save_submission, create_regression_submission
from .strategy_validation import validate_strategy_models

__all__ = [
    "create_regression_submission",
    "expand_predictions_to_submission_format",
    "save_submission",
    "validate_strategy_models",
]

