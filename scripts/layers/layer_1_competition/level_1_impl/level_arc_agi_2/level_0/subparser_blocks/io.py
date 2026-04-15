from typing import Any

from layers.layer_1_competition.level_0_infra.level_1 import (
    add_output_csv_arg,
    add_max_targets_arg,
    add_ensemble_weights_arg,
    add_validation_stacking_toggle,
)


# -------------------------
# Output / artifacts
# -------------------------
def add_output(parser: Any) -> None:
    add_output_csv_arg(parser)


# -------------------------
# Evaluation shaping
# -------------------------
def add_max_targets(parser: Any, default: int = 0) -> None:
    add_max_targets_arg(parser, default=default)


# -------------------------
# Ensemble behavior
# -------------------------
def add_ensemble(parser: Any) -> None:
    add_ensemble_weights_arg(parser)


# -------------------------
# Stacking control
# -------------------------
def add_stacking(parser: Any, default: bool = True) -> None:
    add_validation_stacking_toggle(parser, default=default)