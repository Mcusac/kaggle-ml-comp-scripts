"""Generic CLI argument groups for model-type, model-path, ensemble method."""

import argparse
from typing import Sequence


def add_model_type_argument(
    parser: argparse.ArgumentParser,
    model_type_choices: Sequence[str],
    default: str = "vision",
) -> None:
    parser.add_argument(
        '--model-type',
        choices=model_type_choices,
        default=default,
        help='Model type'
    )


def add_model_path_argument(
    parser: argparse.ArgumentParser,
    required: bool = False,
) -> None:
    parser.add_argument(
        '--model-path',
        type=str,
        required=required,
        help='Model checkpoint path'
    )


def add_ensemble_method_argument(
    parser: argparse.ArgumentParser,
    ensemble_methods: Sequence[str],
    default: str = "weighted_average",
) -> None:
    parser.add_argument(
        '--method',
        choices=ensemble_methods,
        default=default,
        help='Ensembling method'
    )
