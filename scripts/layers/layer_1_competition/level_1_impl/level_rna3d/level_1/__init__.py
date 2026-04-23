"""Auto-generated package exports."""


from .baseline_approx import (
    BaselineApproxConfig,
    BaselineApproxPredictor,
    Template,
    build_templates,
    format_predictions_to_submission_csv,
    group_labels_to_coords,
    make_submission,
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
    "TargetTMScore",
    "Template",
    "build_templates",
    "compute_target_tm_from_arrays",
    "evaluate_predictions_tm",
    "format_predictions_to_submission_csv",
    "group_labels_to_coords",
    "make_submission",
    "run_baseline_approx_predictions",
]
