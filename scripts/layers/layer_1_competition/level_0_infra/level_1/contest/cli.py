"""Common CLI argument helpers for contest subparsers."""

import argparse
from typing import Any, Dict

from ..paths import get_data_root_path


def resolve_handler_args(args: Any, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve handler args from argparse.Namespace with defaults.

    Args:
        args: Parsed argparse namespace
        defaults: Dict mapping arg name -> default value

    Returns:
        Dict of resolved values (getattr(args, k, default) for each key)
    """
    return {k: getattr(args, k, default) for k, default in defaults.items()}


def add_common_contest_args(parser: argparse.ArgumentParser) -> None:
    """
    Add common args shared across contest subparsers.

    Includes: --data-root, --model, --contest, --log-file.
    Contest-specific modules can call this and add more args.
    """
    parser.add_argument("--data-root", type=str, help="Data root directory")
    parser.add_argument("--model", type=str, help="Model name (e.g., efficientnet_b0, dinov2)")
    parser.add_argument("--contest", type=str, help="Contest name")
    parser.add_argument("--log-file", type=str, help="Optional log file path")


def resolve_data_root_from_args(args: Any) -> str:
    """
    Resolve data root from CLI args (``--data-root``) or environment default.

    Unlike ``paths.path_utils.resolve_data_root``, this does not take a
    ``ContestPaths`` instance; it uses ``get_data_root_path()`` when
    ``args.data_root`` is unset.
    """
    return getattr(args, "data_root", None) or get_data_root_path()
