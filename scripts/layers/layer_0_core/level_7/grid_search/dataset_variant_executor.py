"""Variant execution for dataset grid search."""

import copy

from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Union

from layers.layer_0_core.level_0 import (
    ensure_dir,
    get_logger,
    ConfigValidationError,
    MODEL_DIR_DATASET_GRID_SEARCH,
    create_result_dict,
    create_error_result_dict,
)
from layers.layer_0_core.level_1 import cleanup_gpu_memory
from level_6 import create_variant_specific_data

logger = get_logger(__name__)

# Matches level_0 TrainingSchema.batch_size default; used when config lacks batch_size
DEFAULT_BATCH_SIZE = 32


def _create_variant_config(
    config: Union[Any, Dict[str, Any]],
    preprocessing_list: List[str],
    augmentation_list: List[str],
    variant_model_dir: Path
) -> Union[Any, Dict[str, Any]]:
    """
    Create and configure variant-specific config.

    Args:
        config: Base configuration object or dict
        preprocessing_list: List of preprocessing operations
        augmentation_list: List of augmentation operations
        variant_model_dir: Model directory for this variant

    Returns:
        Variant-specific configuration
    """
    variant_config = copy.deepcopy(config)

    # Apply dataset configuration
    if preprocessing_list or augmentation_list:
        logger.debug(f"Applying preprocessing: {preprocessing_list}, augmentation: {augmentation_list}")
        if isinstance(variant_config, dict):
            variant_config['preprocessing_list'] = preprocessing_list
            variant_config['augmentation_list'] = augmentation_list
        elif hasattr(variant_config, 'data'):
            if hasattr(variant_config.data, 'preprocessing_list'):
                variant_config.data.preprocessing_list = preprocessing_list
            if hasattr(variant_config.data, 'augmentation_list'):
                variant_config.data.augmentation_list = augmentation_list
                variant_config.data.use_augmentation = bool(augmentation_list)

    # Update config with model directory
    if isinstance(variant_config, dict):
        variant_config['model_dir'] = str(variant_model_dir)
    elif hasattr(variant_config, 'paths'):
        variant_config.paths.model_dir = str(variant_model_dir)

    return variant_config


def _extract_training_params(
    variant_config: Union[Any, Dict[str, Any]]
) -> Tuple[str, Optional[str], int]:
    """
    Extract data root, model name, and n_folds from variant config.

    Args:
        variant_config: Variant configuration

    Returns:
        Tuple of (data_root, model, n_folds)
    """
    # Get data root from config.paths (set by pipeline from contest_context)
    data_root = None
    if isinstance(variant_config, dict):
        data_root = variant_config.get('data_root')
    if data_root is None and hasattr(variant_config, 'paths'):
        paths = variant_config.paths
        if hasattr(paths, 'get_data_root') and callable(paths.get_data_root):
            root = paths.get_data_root()
            data_root = str(root) if root is not None else None
    if data_root is None:
        raise ConfigValidationError("data_root could not be resolved from variant_config; ensure config.paths has get_data_root()")

    # Get model name
    model = None
    if isinstance(variant_config, dict):
        model = variant_config.get('model') or variant_config.get('model_name')
    elif hasattr(variant_config, 'model'):
        if hasattr(variant_config.model, 'name'):
            model = variant_config.model.name
        elif hasattr(variant_config.model, 'model_name'):
            model = variant_config.model.model_name

    # Get n_folds
    n_folds = 5
    if isinstance(variant_config, dict):
        n_folds = variant_config.get('n_folds', 5)
    elif hasattr(variant_config, 'cv'):
        n_folds = getattr(variant_config.cv, 'n_folds', 5)

    return data_root, model, n_folds


def _create_variant_result(
    config: Union[Any, Dict[str, Any]],
    variant_index: int,
    variant_id: str,
    preprocessing_list: List[str],
    augmentation_list: List[str],
    batch_size_used: int,
    batch_size_reduced: bool,
    cv_score: Optional[float] = None,
    fold_scores: Optional[List[float]] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create result dictionary for variant (success or error).

    Args:
        config: Base configuration
        variant_index: Variant index
        variant_id: Variant ID
        preprocessing_list: Preprocessing operations
        augmentation_list: Augmentation operations
        batch_size_used: Batch size used
        batch_size_reduced: Whether batch size was reduced
        cv_score: Optional CV score (for success)
        fold_scores: Optional fold scores (for success)
        error: Optional error message (for failure)

    Returns:
        Result dictionary
    """
    variant_specific_data = create_variant_specific_data(
        config=config,
        preprocessing_list=preprocessing_list,
        augmentation_list=augmentation_list
    )

    if error:
        return create_error_result_dict(
            variant_index=variant_index,
            variant_id=variant_id,
            error=error,
            batch_size_used=batch_size_used,
            batch_size_reduced=batch_size_reduced,
            variant_specific_data=variant_specific_data
        )
    else:
        return create_result_dict(
            variant_index=variant_index,
            variant_id=variant_id,
            cv_score=cv_score,
            fold_scores=fold_scores,
            batch_size_used=batch_size_used,
            batch_size_reduced=batch_size_reduced,
            variant_specific_data=variant_specific_data
        )


def run_single_variant(
    variant: Tuple[List[str], List[str]],
    variant_index: int,
    total_variants: int,
    config: Union[Any, Dict[str, Any]],
    train_csv_path: Path,
    base_model_dir: Path,
    device: Any,
    results_file: Path,
    train_pipeline_fn: Optional[Any] = None,
) -> Tuple[Optional[float], Optional[List[float]], Dict[str, Any], Path]:
    """
    Run training for a single variant.

    Args:
        variant: Tuple of (preprocessing_list, augmentation_list).
        variant_index: Index of this variant in the grid.
        total_variants: Total number of variants in grid.
        config: Base configuration object or dict.
        train_csv_path: Path to train CSV file.
        base_model_dir: Base model directory.
        device: Device to train on.
        results_file: Path to results JSON file.
        train_pipeline_fn: Callable injected by contest layer; required for training.

    Returns:
        Tuple of (cv_score, fold_scores, result_dict, variant_model_dir).
    """
    preprocessing_list, augmentation_list = variant
    variant_id = f"variant_{variant_index:04d}"

    logger.info("=" * 60)
    logger.info(f"Variant {variant_index+1}/{total_variants}")
    logger.info(f"Preprocessing: {preprocessing_list if preprocessing_list else '[]'}")
    logger.info(f"Augmentation: {augmentation_list if augmentation_list else '[]'}")
    logger.info("=" * 60)

    # Clear GPU memory before starting variant
    cleanup_gpu_memory()

    # Create unique model directory for this variant
    variant_model_dir = base_model_dir / MODEL_DIR_DATASET_GRID_SEARCH / variant_id
    ensure_dir(variant_model_dir)

    # Create variant config
    variant_config = _create_variant_config(
        config, preprocessing_list, augmentation_list, variant_model_dir
    )

    # Track batch size
    batch_size_used = DEFAULT_BATCH_SIZE
    if isinstance(variant_config, dict):
        batch_size_used = variant_config.get('batch_size', DEFAULT_BATCH_SIZE)
    elif hasattr(variant_config, 'training'):
        batch_size_used = getattr(variant_config.training, 'batch_size', DEFAULT_BATCH_SIZE)

    batch_size_reduced = False

    try:
        # Extract training parameters
        data_root, model, n_folds = _extract_training_params(variant_config)

        # Call contest-provided train_pipeline (orchestration must not import contest)
        if train_pipeline_fn is None:
            raise ValueError(
                "train_pipeline_fn is required. Contest layer must pass its train_pipeline when calling dataset grid search."
            )
        cv_score, fold_scores = train_pipeline_fn(
            data_root=data_root,
            model=model,
            n_folds=n_folds,
            **({} if not isinstance(variant_config, dict) else {
                k: v for k, v in variant_config.items()
                if k not in ['data_root', 'model', 'model_name', 'n_folds', 'model_dir']
            })
        )

        # Create success result
        result = _create_variant_result(
            config, variant_index, variant_id, preprocessing_list, augmentation_list,
            batch_size_used, batch_size_reduced, cv_score, fold_scores
        )

        return cv_score, fold_scores, result, variant_model_dir

    except Exception as e:
        logger.error(f"Error training variant {variant_id}: {e}", exc_info=True)

        # Create error result
        result = _create_variant_result(
            config, variant_index, variant_id, preprocessing_list, augmentation_list,
            batch_size_used, batch_size_reduced, error=str(e)
        )

        return None, None, result, variant_model_dir

    finally:
        # Cleanup memory after variant
        cleanup_gpu_memory()
