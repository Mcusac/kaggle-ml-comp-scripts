"""RNA3D contest tier 1: baseline approximation predictor and submission helpers."""

from .baseline_approx import (
    BaselineApproxConfig,
    BaselineApproxPredictor,
    make_submission,
    build_templates,
    group_labels_to_coords,
    format_predictions_to_submission_csv,
    run_baseline_approx_predictions,
)
from .scoring import (
    TargetTMScore,
    compute_target_tm_from_arrays,
    evaluate_predictions_tm,
)

__all__ = [
    "BaselineApproxConfig",
    "BaselineApproxPredictor",
    "build_templates",
    "compute_target_tm_from_arrays",
    "evaluate_predictions_tm",
    "format_predictions_to_submission_csv",
    "group_labels_to_coords",
    "make_submission",
    "run_baseline_approx_predictions",
    "TargetTMScore",
]
