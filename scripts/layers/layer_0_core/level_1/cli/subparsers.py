"""Framework CLI builders."""

import argparse

from typing import AbstractSet, Optional, Sequence

from level_0 import (
    add_common_arguments,
    add_model_type_argument,
    add_model_path_argument,
    add_ensemble_method_argument,
)


def setup_framework_subparsers(
    subparsers: argparse._SubParsersAction,
    model_type_choices: Sequence[str],
    ensemble_methods: Sequence[str],
    skip_commands: Optional[AbstractSet[str]] = None,
) -> None:
    """
    Define all framework-level CLI commands.

    This function only defines CLI structure.
    It does not contain business logic.

    Args:
        skip_commands: Subcommand names to omit so contest handlers can register
            the same name without argparse conflicts (e.g. train, submit).
    """
    skip = skip_commands or frozenset()

    # -----------------
    # Train
    # -----------------
    if 'train' not in skip:
        train = subparsers.add_parser('train', help='Train a model')
        add_common_arguments(train)
        train.add_argument('--batch-size', type=int, help='Batch size')
        train.add_argument('--lr', type=float, help='Learning rate')
        add_model_type_argument(train, model_type_choices)

    # -----------------
    # Test
    # -----------------
    test = subparsers.add_parser('test', help='Test/Predict with trained model')
    add_common_arguments(test)
    add_model_path_argument(test, required=True)
    add_model_type_argument(test, model_type_choices)
    test.add_argument('--use-tta', action='store_true', help='Use test-time augmentation')

    # -----------------
    # Train + Test
    # -----------------
    train_test = subparsers.add_parser('train_test', help='Train and test')
    add_common_arguments(train_test)
    add_model_type_argument(train_test, model_type_choices)

    # -----------------
    # Grid Search
    # -----------------
    grid = subparsers.add_parser('grid_search', help='Run hyperparameter search')
    add_common_arguments(grid)
    grid.add_argument(
        '--search-type',
        choices=['quick', 'in_depth'],
        default='quick',
        help='Grid search type'
    )
    add_model_type_argument(grid, model_type_choices)

    # -----------------
    # Cross Validation
    # -----------------
    cv = subparsers.add_parser('cross_validate', help='Run k-fold cross-validation')
    add_common_arguments(cv)
    cv.add_argument('--n-folds', type=int, default=5, help='Number of folds')
    add_model_type_argument(cv, model_type_choices)

    # -----------------
    # Ensemble
    # -----------------
    ensemble = subparsers.add_parser('ensemble', help='Generate ensemble predictions')
    add_common_arguments(ensemble)
    ensemble.add_argument('--model-paths', type=str, required=True, help='Comma-separated model paths')
    add_ensemble_method_argument(ensemble, ensemble_methods)
    ensemble.add_argument('--weights', type=str, help='Comma-separated weights')

    # -----------------
    # Export
    # -----------------
    export = subparsers.add_parser('export', help='Export trained model')
    add_common_arguments(export)
    add_model_path_argument(export, required=True)
    export.add_argument('--export-dir', type=str, required=True, help='Export directory')

    # -----------------
    # Submit
    # -----------------
    if 'submit' not in skip:
        submit = subparsers.add_parser('submit', help='Submit predictions')
        add_common_arguments(submit)
        add_model_path_argument(submit)
        submit.add_argument(
            '--strategy',
            choices=['single', 'ensemble', 'stacking', 'stacking_ensemble'],
            default='single',
            help='Submission strategy'
        )
        submit.add_argument('--models', type=str, help='Comma-separated model names')
        submit.add_argument('--ensemble-weights', type=str, help='Comma-separated weights')
        submit.add_argument('--use-validation-for-stacking', action='store_true')
        submit.add_argument('--max-targets', type=int)
        submit.add_argument('--output-csv', type=str)
