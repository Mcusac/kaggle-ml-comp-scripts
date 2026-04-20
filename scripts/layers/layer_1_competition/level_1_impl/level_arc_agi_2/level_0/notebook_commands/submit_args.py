"""ARC notebook command submit arguments (composite wrapper over infra primitives)."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0 import (
    append_ensemble_weights,
    append_max_targets,
    append_no_validation_stacking,
    append_output_csv,
)


def append_submit_args(
    cmd: List[str],
    output_csv: Optional[str],
    max_targets: int,
    ensemble_weights: Optional[List[float]],
    use_validation_for_stacking: bool,
) -> None:
    """Append the submit-specific argv tokens (output, targets, ensemble, validation)."""
    append_output_csv(cmd, output_csv)
    append_max_targets(cmd, max_targets)
    append_ensemble_weights(cmd, ensemble_weights)
    append_no_validation_stacking(cmd, use_validation_for_stacking)