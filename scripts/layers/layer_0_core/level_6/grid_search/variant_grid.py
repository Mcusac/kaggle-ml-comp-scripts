"""Variant key and variant-specific data for grid search pipelines."""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

from level_0 import DATASET_TYPE_SPLIT, get_logger
from level_1 import get_transformer_hyperparameter_grid
from level_5 import find_metadata_dir

logger = get_logger(__name__)


def get_default_hyperparameters() -> Dict[str, Any]:
    """Return default transformer hyperparameters (first value from each grid)."""
    defaults_grid = get_transformer_hyperparameter_grid("defaults")
    return {k: v[0] for k, v in defaults_grid.items()}


def _extract_dataset_type(config: Union[Any, Dict[str, Any]]) -> str:
    """Extract dataset_type from config object or dict."""
    if isinstance(config, dict):
        return config.get("dataset_type", DATASET_TYPE_SPLIT)
    data = getattr(config, "data", None)
    return getattr(data, "dataset_type", None) or DATASET_TYPE_SPLIT


def create_variant_specific_data(
    config: Union[Any, Dict[str, Any]],
    preprocessing_list: Optional[List[str]] = None,
    augmentation_list: Optional[List[str]] = None,
    hyperparameters: Optional[Dict[str, Any]] = None,
    feature_filename: Optional[str] = None,
    metadata_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Create variant-specific data dictionary for grid search results.

    Args:
        config: Configuration object or dict.
        preprocessing_list: Optional list of preprocessing techniques.
        augmentation_list: Optional list of augmentation techniques.
        hyperparameters: Optional dictionary of hyperparameters.
        feature_filename: Optional feature filename (for regression searches).
        metadata_dir: Optional metadata directory path.

    Returns:
        Dictionary with variant-specific data.
    """
    dataset_type = _extract_dataset_type(config)
    variant_specific_data = {"dataset_type": dataset_type}

    if preprocessing_list is not None and augmentation_list is not None:
        variant_specific_data["preprocessing_list"] = preprocessing_list
        variant_specific_data["augmentation_list"] = augmentation_list

        if metadata_dir is None:
            metadata_dir = find_metadata_dir()

        if metadata_dir:
            logger.debug(
                "combo_id lookup skipped: get_or_create_combo_id not available"
            )
        else:
            logger.warning("Metadata directory not found, cannot resolve combo_id")

    if hyperparameters is not None:
        variant_specific_data["hyperparameters"] = hyperparameters
    else:
        defaults_grid = get_transformer_hyperparameter_grid("defaults")
        variant_specific_data["hyperparameters"] = {
            k: v[0] for k, v in defaults_grid.items()
        }

    if feature_filename is not None:
        variant_specific_data["feature_filename"] = feature_filename

    return variant_specific_data


def create_variant_key(
    config: Union[Any, Dict[str, Any]],
    preprocessing_list: List[str],
    augmentation_list: List[str],
    hyperparameters: Dict[str, Any],
) -> Tuple[str, Tuple[str, ...], Tuple[str, ...], Tuple[Tuple[str, Any], ...]]:
    """
    Create variant key for deduplication in grid searches.

    Args:
        config: Configuration object or dict.
        preprocessing_list: List of preprocessing techniques.
        augmentation_list: List of augmentation techniques.
        hyperparameters: Dictionary of hyperparameters.

    Returns:
        Tuple of (dataset_type, prep_key, aug_key, hyperparams_key).
    """
    dataset_type = _extract_dataset_type(config)
    prep_key = tuple(sorted(preprocessing_list))
    aug_key = tuple(sorted(augmentation_list))
    hyperparams_key = tuple(sorted(hyperparameters.items()))
    return (dataset_type, prep_key, aug_key, hyperparams_key)


def create_variant_key_from_result(
    result: Dict[str, Any],
    config: Optional[Union[Any, Dict[str, Any]]] = None,
) -> Optional[Tuple[str, Tuple[str, ...], Tuple[str, ...], Tuple[Tuple[str, Any], ...]]]:
    """
    Create variant key from result dictionary for dataset/hyperparameter grid searches.

    Args:
        result: Result dictionary from grid search results file.
        config: Optional configuration object or dict.

    Returns:
        Variant key tuple if successful, None otherwise.
    """
    dataset_type = (
        _extract_dataset_type(config)
        if config is not None
        else result.get("dataset_type", DATASET_TYPE_SPLIT)
    )

    preprocessing_list = result.get("preprocessing_list", [])
    augmentation_list = result.get("augmentation_list", [])

    if not preprocessing_list or not augmentation_list:
        data_manipulation = result.get("data_manipulation", {})
        if data_manipulation:
            preprocessing_list = data_manipulation.get("preprocessing_list", [])
            augmentation_list = data_manipulation.get("augmentation_list", [])

    prep_key = tuple(sorted(preprocessing_list))
    aug_key = tuple(sorted(augmentation_list))
    hyperparams_key = tuple(sorted(result.get("hyperparameters", {}).items()))
    return (dataset_type, prep_key, aug_key, hyperparams_key)


def create_regression_variant_key_from_result(
    result: Dict[str, Any],
) -> Optional[Tuple[str, Tuple[Tuple[str, Any], ...]]]:
    """
    Create variant key from result dictionary for regression grid searches.

    Args:
        result: Result dictionary from regression grid search results file.

    Returns:
        Variant key tuple (feature_filename, hyperparams_key) if successful, None otherwise.
    """
    if "hyperparameters" not in result:
        return None

    feature_filename = result.get("feature_filename")
    if feature_filename is None:
        return None

    hyperparams_key = tuple(sorted(result.get("hyperparameters", {}).items()))
    return (feature_filename, hyperparams_key)
