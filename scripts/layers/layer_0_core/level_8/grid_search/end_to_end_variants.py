"""End-to-end grid search: variant config extraction and result dict builders."""

import copy
from typing import Any, Dict, Optional, Tuple

from layers.layer_0_core.level_0 import ConfigValidationError
from layers.layer_0_core.level_7 import build_error_result, build_success_result

DEFAULT_BATCH_SIZE = 32


def _apply_hyperparameters_to_config(config: Any, hyperparameters: Dict[str, Any]) -> None:
    """Apply hyperparameters to config object in place."""
    for key, value in hyperparameters.items():
        if hasattr(config, 'training') and hasattr(config.training, key):
            setattr(config.training, key, value)
        elif hasattr(config, key):
            setattr(config, key, value)


def extract_variant_config(
    variant_config: Any,
    param_names: list,
    variant: tuple,
    variant_index: int
) -> Tuple[Any, str, int, int, str, str]:
    """
    Extract configuration values from variant config.

    Args:
        variant_config: Configuration object or dict
        param_names: Parameter names
        variant: Variant tuple
        variant_index: Index of variant in grid (used for variant_id)

    Returns:
        Tuple of (variant_config_copy, model_name, n_folds, batch_size, variant_id, data_root)
    """
    # Create hyperparameters dict
    hyperparameters = dict(zip(param_names, variant))

    # Create config copy for this variant
    variant_config_copy = copy.deepcopy(variant_config)

    # Apply hyperparameters to config
    _apply_hyperparameters_to_config(variant_config_copy, hyperparameters)

    # Resolve data root from config.paths (set by pipeline from contest_context)
    data_root = None
    if isinstance(variant_config_copy, dict):
        data_root = variant_config_copy.get('data_root')
    if data_root is None and hasattr(variant_config_copy, 'paths') and hasattr(variant_config_copy.paths, 'get_data_root'):
        root = variant_config_copy.paths.get_data_root()
        data_root = str(root) if root is not None else None
    if data_root is None:
        raise ConfigValidationError("data_root could not be resolved; ensure config.paths has get_data_root()")

    # Get model name
    model = None
    if isinstance(variant_config_copy, dict):
        model = variant_config_copy.get('model') or variant_config_copy.get('model_name')
    elif hasattr(variant_config_copy, 'model'):
        if hasattr(variant_config_copy.model, 'name'):
            model = variant_config_copy.model.name
        elif hasattr(variant_config_copy.model, 'model_name'):
            model = variant_config_copy.model.model_name

    # Get training parameters
    n_folds = 5
    if isinstance(variant_config_copy, dict):
        n_folds = variant_config_copy.get('n_folds', 5)
    elif hasattr(variant_config_copy, 'cv'):
        n_folds = getattr(variant_config_copy.cv, 'n_folds', 5)

    # Get batch size
    batch_size_used = DEFAULT_BATCH_SIZE
    if isinstance(variant_config_copy, dict):
        batch_size_used = variant_config_copy.get('batch_size', DEFAULT_BATCH_SIZE)
    elif hasattr(variant_config_copy, 'training'):
        batch_size_used = getattr(variant_config_copy.training, 'batch_size', DEFAULT_BATCH_SIZE)

    variant_id = f"variant_{variant_index:04d}"

    return variant_config_copy, model, n_folds, batch_size_used, variant_id, data_root


def create_end_to_end_variant_result(
    variant_index: int,
    variant_id: str,
    cv_score: Optional[float],
    fold_scores: Optional[list],
    hyperparameters: Dict[str, Any],
    config: Any,
    batch_size_used: int,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create result dictionary for end-to-end variant.

    Args:
        variant_index: Variant index
        variant_id: Variant ID
        cv_score: Average CV score (if successful)
        fold_scores: List of fold scores (if successful)
        hyperparameters: Hyperparameters used
        config: Configuration object
        batch_size_used: Batch size used
        error: Error message if failed

    Returns:
        Result dictionary
    """

    if error:
        return build_error_result(
            variant_index=variant_index,
            variant_id=variant_id,
            error=error,
            batch_size_used=batch_size_used,
            batch_size_reduced=False,
            config=config,
            hyperparameters=hyperparameters,
        )
    return build_success_result(
        variant_index=variant_index,
        variant_id=variant_id,
        cv_score=cv_score,
        fold_scores=fold_scores,
        batch_size_used=batch_size_used,
        batch_size_reduced=False,
        config=config,
        hyperparameters=hyperparameters,
    )
