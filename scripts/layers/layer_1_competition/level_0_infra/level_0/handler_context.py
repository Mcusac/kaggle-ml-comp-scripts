"""Shared handler context helpers (no command-specific logic)."""

import argparse

from typing import Any

from layers.layer_0_core.level_0 import get_arg


def setup_handler_context(
    *,
    args: argparse.Namespace,
    builder: Any,
) -> tuple[str, Any, str, Any, Any, Any]:
    """Set up common context for command handlers using injected builder."""
    contest_name = builder.detect_contest(args)
    config = builder.get_config(contest_name, args)
    model_type = get_arg(args, "model_type", "vision")
    config.model.type = model_type
    data_schema = builder.get_data_schema(contest_name)
    paths = builder.get_paths(contest_name)
    contest = {"paths": lambda: paths, "data_schema": lambda: data_schema}
    return contest_name, config, model_type, contest, data_schema, paths

