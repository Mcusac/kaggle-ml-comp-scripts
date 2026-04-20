"""Register ARC-AGI-2 contest subparsers on the framework ``run.py`` parser."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    add_validate_data_subparser,
    add_postprocess_subparsers,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    add_submit_subparser,
    add_train_subparser,
    add_train_and_submit_subparser,
    add_tune_subparser,
    add_tune_and_submit_subparser,
)


def extend_subparsers(subparsers: Any) -> None:
    """Add ARC contest subcommands (framework skips ``train`` / ``submit`` names)."""
    add_validate_data_subparser(subparsers)
    add_train_subparser(subparsers)
    add_tune_subparser(subparsers)
    add_submit_subparser(subparsers)
    add_postprocess_subparsers(subparsers)
    add_train_and_submit_subparser(subparsers)
    add_tune_and_submit_subparser(subparsers)
