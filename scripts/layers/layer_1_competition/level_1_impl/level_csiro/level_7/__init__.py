"""CSIRO level_7: CLI facade (subparsers + handler registry + multi-variant pipeline)."""

from .multi_variant_regression_training_pipeline import (
    multi_variant_regression_training_pipeline,
)

from .handlers import (
    extend_subparsers,
    get_handlers,
    handle_cleanup_grid_search,
    handle_csiro_ensemble,
    handle_dataset_grid_search,
    handle_export_model,
    handle_hyperparameter_grid_search,
    handle_hybrid_stacking,
    handle_multi_variant_regression_train,
    handle_regression_ensemble,
    handle_regression_grid_search,
    handle_stacking,
    handle_stacking_ensemble,
    handle_submit,
    handle_submit_best,
    handle_train_and_export,
)

__all__ = [
    "extend_subparsers",
    "get_handlers",
    "multi_variant_regression_training_pipeline",
    "handle_cleanup_grid_search",
    "handle_csiro_ensemble",
    "handle_dataset_grid_search",
    "handle_export_model",
    "handle_hyperparameter_grid_search",
    "handle_hybrid_stacking",
    "handle_multi_variant_regression_train",
    "handle_regression_ensemble",
    "handle_regression_grid_search",
    "handle_stacking",
    "handle_stacking_ensemble",
    "handle_submit",
    "handle_submit_best",
    "handle_train_and_export",
]
