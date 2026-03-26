"""Helper functions for CLI parser setup."""

from typing import Any


def add_grid_search_parsers(subparsers: Any, _add_common: Any) -> None:
    """Add grid search related subparsers."""
    # Dataset grid search
    p = subparsers.add_parser('dataset_grid_search', help='Dataset grid search (preprocessing/augmentation)')
    _add_common(p)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')
    p.add_argument('--max-augmentation', action='store_true', default=False)

    # Hyperparameter grid search
    p = subparsers.add_parser('hyperparameter_grid_search', help='Hyperparameter grid search (fixed dataset config)')
    _add_common(p)
    p.add_argument('--search-type', choices=['defaults', 'quick', 'in_depth', 'thorough', 'focused_in_depth', 'focused_thorough'], default='thorough')
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')
    p.add_argument('--metadata-path', type=str)
    p.add_argument('--results-file', type=str)
    p.add_argument('--previous-results-file', type=str)

    # Regression grid search
    p = subparsers.add_parser('regression_grid_search', help='Regression hyperparameter grid search (pre-extracted features)')
    _add_common(p)
    p.add_argument('--feature-filename', type=str, required=True)
    p.add_argument('--regression-model-type', type=str, choices=['lgbm', 'xgboost', 'ridge'], default='lgbm')
    p.add_argument('--search-type', choices=['defaults', 'quick', 'in_depth', 'thorough'], default='quick')

    # Cleanup grid search
    p = subparsers.add_parser('cleanup_grid_search', help='Clean up grid search checkpoints')
    p.add_argument('--model-dir', type=str)
    p.add_argument('--results-file', type=str)
    p.add_argument('--keep-top', type=int, default=20)


def add_training_parsers(subparsers: Any, _add_common: Any) -> None:
    """Add training and export related subparsers."""
    # Train and export
    p = subparsers.add_parser('train_and_export', help='Train and export for submission (Pipeline C)')
    _add_common(p)
    p.add_argument('--results-file', type=str)
    p.add_argument('--variant-id', type=str)
    p.add_argument('--export-dir', type=str)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')
    p.add_argument('--fresh-train', action='store_true', default=False)
    p.add_argument('--export-only', action='store_true', default=False)
    p.add_argument('--feature-extraction-mode', action='store_true', default=False)
    p.add_argument('--feature-extraction-model', type=str)
    p.add_argument('--regression-model-type', type=str, choices=['lgbm', 'xgboost', 'ridge'])
    p.add_argument('--regression-model-variant-id', type=str)
    p.add_argument('--extract-features', action='store_true', default=None)
    p.add_argument('--data-manipulation-combo', type=str)
    p.add_argument('--no-extract-features', dest='extract_features', action='store_false')

    # Export model (CSIRO-specific)
    p = subparsers.add_parser('export_model', help='Export trained model for submission')
    _add_common(p)
    p.add_argument('--results-file', type=str)
    p.add_argument('--variant-id', type=str)
    p.add_argument('--best-variant-file', type=str)
    p.add_argument('--export-dir', type=str)

    # Multi-variant regression train
    p = subparsers.add_parser('multi_variant_regression_train', help='Train multiple regression models, one per model_id')
    _add_common(p)
    p.add_argument('--feature-extraction-model', type=str, required=True)
    p.add_argument('--regression-model-type', type=str, required=True, choices=['lgbm', 'xgboost', 'ridge'])
    p.add_argument('--model-ids', type=str, required=True)
    p.add_argument('--extract-features', action='store_true', default=None)
    p.add_argument('--no-extract-features', dest='extract_features', action='store_false')
    p.add_argument('--data-manipulation-combo', type=str)
    p.add_argument('--fresh-train', action='store_true')
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')


def add_ensemble_parsers(subparsers: Any, _add_common: Any) -> None:
    """Add ensemble related subparsers."""
    # csiro_ensemble: top-N from grid search / model paths
    p = subparsers.add_parser('csiro_ensemble', help='Ensemble of top N models from grid search (CSIRO)')
    _add_common(p)
    p.add_argument('--model-paths', type=str)
    p.add_argument('--results-files', type=str)
    p.add_argument('--top-n', type=int, default=3)
    p.add_argument('--method', choices=['simple_average', 'weighted_average', 'ranked_average', 'percentile_average'], default='weighted_average')
    p.add_argument('--fallback-paths', type=str)
    p.add_argument('--submission-scores', type=str)
    p.add_argument('--score-type', choices=['cv', 'submission', 'combined'], default='cv')
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')

    # Regression ensemble
    p = subparsers.add_parser('regression_ensemble', help='Ensemble of regression models (LGBM, XGBoost, Ridge)')
    _add_common(p)
    p.add_argument('--ensemble-config', type=str, required=True)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')

    # Stacking
    p = subparsers.add_parser('stacking', help='Stacking with Ridge meta-model')
    _add_common(p)
    p.add_argument('--stacking-config', type=str, required=True)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')

    # Stacking ensemble
    p = subparsers.add_parser('stacking_ensemble', help='Stacking with ensemble base models')
    _add_common(p)
    p.add_argument('--stacking-ensemble-config', type=str, required=True)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')

    # Hybrid stacking
    p = subparsers.add_parser('hybrid_stacking', help='Hybrid stacking (regression + end-to-end ensembles)')
    _add_common(p)
    p.add_argument('--hybrid-stacking-config', type=str, required=True)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')


def add_submission_parsers(subparsers: Any, _add_common: Any) -> None:
    """Add submission related subparsers."""
    # Submit best
    p = subparsers.add_parser('submit_best', help='Submit best variant from dataset grid search')
    _add_common(p)
    p.add_argument('--variant-id', type=str)
    p.add_argument('--results-file', type=str)

    # Submit (Pipeline A - offline from uploaded model)
    p = subparsers.add_parser('submit', help='Generate submission from uploaded model (Pipeline A)')
    _add_common(p)
    p.add_argument('--model-path', type=str)
    p.add_argument('--metadata-path', type=str)
    p.add_argument('--results-file', type=str)
    p.add_argument('--model-name', type=str)
    p.add_argument('--dataset-type', type=str, choices=['full', 'split'], default='split')
