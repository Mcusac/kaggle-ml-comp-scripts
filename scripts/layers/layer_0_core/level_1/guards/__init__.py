"""Invariant guard utilities.

This package contains pure invariant enforcement utilities.
Guards raise exceptions on failure and return None on success.

Rules:
- No runtime interpretation
- No orchestration logic
- No search-specific validation
- Only structural and data invariants
"""

from .arrays import check_array_finite
from .collections import check_min_collection_length
from .config import (
    validate_config_section_exists,
    validate_feature_extraction_trainer_inputs,
)
from .ensembles import validate_predictions_for_ensemble, validate_paired_predictions
from .none import check_not_none
from .result_checks import validate_execution_result

__all__ = [
    "check_array_finite",
    "check_min_collection_length",
    "validate_config_section_exists",
    "validate_feature_extraction_trainer_inputs",
    "validate_predictions_for_ensemble",
    "validate_paired_predictions",
    "check_not_none",
    "validate_execution_result",
]