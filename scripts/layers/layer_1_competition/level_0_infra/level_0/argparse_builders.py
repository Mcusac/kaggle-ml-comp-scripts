"""Small argparse flag builders shared across contest CLIs.

These helpers only add flags; they do not encode contest-specific policy.
"""

import argparse
from typing import Iterable, Optional


def add_train_mode_arg(
    parser: argparse.ArgumentParser,
    *,
    default: str = "end_to_end",
    help_text: Optional[str] = "Training pipeline label (e.g. end_to_end, multi_part)",
) -> None:
    kwargs = {"type": str, "default": default}
    if help_text is not None:
        kwargs["help"] = help_text
    parser.add_argument("--train-mode", **kwargs)


def add_models_arg(
    parser: argparse.ArgumentParser,
    *,
    default: str = "baseline_approx",
    help_text: Optional[str] = "Comma-separated model names (e.g. baseline_approx)",
) -> None:
    kwargs = {"type": str, "default": default}
    if help_text is not None:
        kwargs["help"] = help_text
    parser.add_argument("--models", **kwargs)


def add_max_targets_arg(
    parser: argparse.ArgumentParser,
    *,
    default: int = 0,
    help_text: Optional[str] = "If >0, only use the first N targets",
) -> None:
    kwargs = {"type": int, "default": int(default)}
    if help_text is not None:
        kwargs["help"] = help_text
    parser.add_argument("--max-targets", **kwargs)


def add_output_csv_arg(
    parser: argparse.ArgumentParser,
    *,
    help_text: Optional[str] = "Optional output CSV path",
) -> None:
    kwargs = {"type": str}
    if help_text is not None:
        kwargs["help"] = help_text
    parser.add_argument("--output-csv", **kwargs)


def add_strategy_arg(
    parser: argparse.ArgumentParser,
    *,
    choices: Iterable[str] = ("single", "ensemble", "stacking", "stacking_ensemble"),
    default: str = "single",
    help_text: Optional[str] = "Submission strategy",
) -> None:
    kwargs = {"choices": list(choices), "default": default}
    if help_text is not None:
        kwargs["help"] = help_text
    parser.add_argument("--strategy", **kwargs)


def add_ensemble_weights_arg(
    parser: argparse.ArgumentParser,
    *,
    help_text: Optional[str] = "Comma-separated weights for ensemble/stacking",
) -> None:
    kwargs = {"type": str}
    if help_text is not None:
        kwargs["help"] = help_text
    parser.add_argument("--ensemble-weights", **kwargs)


def add_validation_stacking_toggle(
    parser: argparse.ArgumentParser,
    *,
    default: bool = True,
    flag_name: str = "--no-validation-stacking",
    dest: str = "use_validation_for_stacking",
    help_text: Optional[str] = None,
) -> None:
    """
    Add a stacking toggle with the common convention:
      - default `use_validation_for_stacking=True`
      - `--no-validation-stacking` flips it to False
    """
    parser.set_defaults(**{dest: bool(default)})
    parser.add_argument(
        flag_name,
        dest=dest,
        action="store_false",
        help=help_text,
    )


__all__ = [
    "add_ensemble_weights_arg",
    "add_max_targets_arg",
    "add_models_arg",
    "add_output_csv_arg",
    "add_strategy_arg",
    "add_train_mode_arg",
    "add_validation_stacking_toggle",
]