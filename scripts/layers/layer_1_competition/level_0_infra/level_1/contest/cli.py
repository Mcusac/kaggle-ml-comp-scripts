"""Common CLI argument helpers for contest subparsers."""

import argparse
from typing import Any, Dict, List, Optional

from layers.layer_1_competition.level_0_infra.level_1.paths import get_data_root_path


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


def parse_models_csv(raw: Optional[str], *, default: Optional[List[str]] = None) -> List[str]:
    """
    Parse comma-separated model names from a CLI flag.

    Behavior is intentionally minimal and stable:
    - Empty/whitespace input returns ``default`` (or ``["baseline_approx"]`` when unset).
    - Otherwise, splits by comma and strips whitespace, dropping empty pieces.
    """
    if not raw or not str(raw).strip():
        return list(default) if default is not None else ["baseline_approx"]
    return [piece.strip() for piece in str(raw).split(",") if piece.strip()]


def parse_optional_float_list(raw: Optional[str]) -> Optional[List[float]]:
    """
    Parse comma-separated floats from a CLI flag.

    Returns None when the input is empty/whitespace; otherwise returns a list of floats.
    """
    if not raw or not str(raw).strip():
        return None
    return [float(x.strip()) for x in str(raw).split(",") if x.strip()]


def parse_weights_csv(raw: Optional[str]) -> Optional[List[float]]:
    """Semantic alias for `parse_optional_float_list` for ensemble/stacking weights."""
    return parse_optional_float_list(raw)
