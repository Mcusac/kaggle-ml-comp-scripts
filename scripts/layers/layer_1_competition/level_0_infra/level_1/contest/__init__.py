"""Contest CLI, context, and data-loading surface for infra level_1."""

from layers.layer_0_core.level_1.pipelines import (
    BasePipeline,
    TwoStageValidateFirstPipelineResultShell,
    ValidateFirstPipelineResultShell,
    ValidateFirstRunner,
)

from .cli import (
    add_common_contest_args,
    parse_models_csv,
    parse_optional_float_list,
    parse_weights_csv,
    resolve_data_root_from_args,
    resolve_handler_args,
)
from .context import ContestContext, build_contest_context
from .csv_io import load_training_csv
from .splits import split_train_val
from .data_loading import load_contest_data, load_contest_training_data
from layers.layer_1_competition.level_0_infra.level_0.argparse_builders import (
    add_ensemble_weights_arg,
    add_max_targets_arg,
    add_models_arg,
    add_output_csv_arg,
    add_strategy_arg,
    add_train_mode_arg,
    add_validation_stacking_toggle,
)

__all__ = [
    "add_common_contest_args",
    "build_contest_context",
    "ContestContext",
    "load_contest_data",
    "load_contest_training_data",
    "load_training_csv",
    "parse_models_csv",
    "parse_optional_float_list",
    "parse_weights_csv",
    "resolve_data_root_from_args",
    "resolve_handler_args",
    "split_train_val",
    "add_ensemble_weights_arg",
    "add_max_targets_arg",
    "add_models_arg",
    "add_output_csv_arg",
    "add_strategy_arg",
    "add_train_mode_arg",
    "add_validation_stacking_toggle",
    "BasePipeline",
    "ValidateFirstRunner",
    "ValidateFirstPipelineResultShell",
    "TwoStageValidateFirstPipelineResultShell",
]
