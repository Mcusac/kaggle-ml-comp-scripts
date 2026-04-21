"""Notebook-facing command builders for ARC-AGI-2 (lazy imports avoid ``cmd_*`` cycles)."""

from __future__ import annotations

from typing import Any

from .base_cmd import base_cmd
from .llm_args import append_llm
from .submit_args import append_submit_args

__all__ = [
    "append_llm",
    "append_submit_args",
    "base_cmd",
    "build_submit_command",
    "build_train_and_submit_command",
    "build_train_command",
    "build_tune_and_submit_command",
    "build_tune_command",
    "build_validate_data_command",
]


def __getattr__(name: str) -> Any:
    if name == "build_validate_data_command":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.notebook_commands.cmd_validate_data import (
            build_validate_data_command,
        )

        return build_validate_data_command
    if name == "build_train_command":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.notebook_commands.cmd_train import (
            build_train_command,
        )

        return build_train_command
    if name == "build_tune_command":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.notebook_commands.cmd_tune import (
            build_tune_command,
        )

        return build_tune_command
    if name == "build_submit_command":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.cmd_submit import (
            build_submit_command,
        )

        return build_submit_command
    if name == "build_train_and_submit_command":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.cmd_train_and_submit import (
            build_train_and_submit_command,
        )

        return build_train_and_submit_command
    if name == "build_tune_and_submit_command":
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.cmd_tune_and_submit import (
            build_tune_and_submit_command,
        )

        return build_tune_and_submit_command
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
