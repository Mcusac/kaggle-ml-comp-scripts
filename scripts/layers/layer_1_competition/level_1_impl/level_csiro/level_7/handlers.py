"""CSIRO contest-specific CLI: extend_subparsers and get_handlers.

See contest/CLI_EXTENSION.md for the contract. Subcommands are loaded only
when --contest csiro (or KAGGLE_COMP_CONTEST=csiro or auto-detect).

Facade that delegates to focused handler modules.
"""

import argparse

from typing import Any, Callable, Dict

from layers.layer_1_competition.level_0_infra.level_0 import (
    add_grid_search_parsers,
    add_training_parsers,
    add_ensemble_parsers,
    add_submission_parsers,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import add_common_args
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import (
    handle_csiro_ensemble,
    handle_regression_ensemble,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_5 import (
    handle_cleanup_grid_search,
    handle_dataset_grid_search,
    handle_export_model,
    handle_hybrid_stacking,
    handle_hyperparameter_grid_search,
    handle_regression_grid_search,
    handle_stacking,
    handle_stacking_ensemble,
    handle_submit,
    handle_submit_best,
    handle_train_and_export,
)
from .handlers_multi_variant import handle_multi_variant_regression_train

FRAMEWORK_SUBPARSER_NAMES_TO_SKIP = frozenset({"submit"})


def extend_subparsers(subparsers: Any) -> None:
    """Add CSIRO contest subparsers. Called by run.py after framework subparsers."""
    add_grid_search_parsers(subparsers, add_common_args)
    add_training_parsers(subparsers, add_common_args)
    add_ensemble_parsers(subparsers, add_common_args)
    add_submission_parsers(subparsers, add_common_args)


def get_handlers() -> Dict[str, Callable[[argparse.Namespace], None]]:
    """Return command -> handler for CSIRO contest subcommands."""
    return {
        "dataset_grid_search": handle_dataset_grid_search,
        "hyperparameter_grid_search": handle_hyperparameter_grid_search,
        "regression_grid_search": handle_regression_grid_search,
        "cleanup_grid_search": handle_cleanup_grid_search,
        "submit_best": handle_submit_best,
        "train_and_export": handle_train_and_export,
        "export_model": handle_export_model,
        "csiro_ensemble": handle_csiro_ensemble,
        "regression_ensemble": handle_regression_ensemble,
        "stacking": handle_stacking,
        "stacking_ensemble": handle_stacking_ensemble,
        "hybrid_stacking": handle_hybrid_stacking,
        "multi_variant_regression_train": handle_multi_variant_regression_train,
        "submit": handle_submit,
    }
