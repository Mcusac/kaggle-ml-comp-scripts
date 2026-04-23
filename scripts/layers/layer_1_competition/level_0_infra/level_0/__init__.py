"""Auto-generated mixed exports."""


from . import (
    abstractions,
    artifacts,
    cli,
    llm_tta_args,
    lm,
    model,
    paths,
    pipeline,
    run_tracking,
    runner,
    submission,
)

from .abstractions import *
from .artifacts import *
from .cli import *
from .llm_tta_args import *
from .lm import *
from .model import *
from .paths import *
from .pipeline import *
from .run_tracking import *
from .runner import *
from .submission import *

from .argparse_builders import (
    add_ensemble_weights_arg,
    add_max_targets_arg,
    add_models_arg,
    add_output_csv_arg,
    add_strategy_arg,
    add_train_mode_arg,
    add_validation_stacking_toggle,
)

from .argv_command_builders import (
    append_ensemble_weights,
    append_llm_args,
    append_max_targets,
    append_models,
    append_no_validation_stacking,
    append_output_csv,
    append_run_args,
    append_strategy,
    append_train_mode,
    append_tune_args,
    append_tuned_config,
    llm_tta_kwargs_from_args,
    resolve_and_append_models,
    resolve_models,
)

from .context_types import ContestGridSearchContext

from .dispatch import (
    get_notebook_commands_module,
    list_contests_with_notebook_commands,
    register_notebook_commands_module,
)

from .ensemble import make_handler

from .grid_ops import (
    arc_grids_equal,
    cell_match_counts,
    grid_int_hash_key,
    score_grid_exact_match,
)

from .handler_context import setup_handler_context

from .pipeline_logging import log_result

from .streaming import run_cli_streaming

__all__ = (
    list(abstractions.__all__)
    + list(artifacts.__all__)
    + list(cli.__all__)
    + list(llm_tta_args.__all__)
    + list(lm.__all__)
    + list(model.__all__)
    + list(paths.__all__)
    + list(pipeline.__all__)
    + list(run_tracking.__all__)
    + list(runner.__all__)
    + list(submission.__all__)
    + [
        "ContestGridSearchContext",
        "add_ensemble_weights_arg",
        "add_max_targets_arg",
        "add_models_arg",
        "add_output_csv_arg",
        "add_strategy_arg",
        "add_train_mode_arg",
        "add_validation_stacking_toggle",
        "append_ensemble_weights",
        "append_llm_args",
        "append_max_targets",
        "append_models",
        "append_no_validation_stacking",
        "append_output_csv",
        "append_run_args",
        "append_strategy",
        "append_train_mode",
        "append_tune_args",
        "append_tuned_config",
        "arc_grids_equal",
        "cell_match_counts",
        "get_notebook_commands_module",
        "grid_int_hash_key",
        "list_contests_with_notebook_commands",
        "llm_tta_kwargs_from_args",
        "log_result",
        "make_handler",
        "register_notebook_commands_module",
        "resolve_and_append_models",
        "resolve_models",
        "run_cli_streaming",
        "score_grid_exact_match",
        "setup_handler_context",
    ]
)
