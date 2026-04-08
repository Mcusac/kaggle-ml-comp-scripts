"""Hyperparameter analysis utilities for ML model tuning.

This module provides utilities for analyzing hyperparameters from grid search results,
following DRY principles by reusing existing framework functions where possible.
"""

from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
from pathlib import Path

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json
from layers.layer_0_core.level_5.file_io.merge import (
    merge_json_from_input_and_working,
    merge_list_by_key_working_replaces,
)
from layers.layer_0_core.level_5.metadata.paths import (
    find_metadata_dir,
    get_writable_metadata_dir,
)

logger = get_logger(__name__)

# Hyperparameter constants for different model types
LGBM_HYPERPARAMETERS = [
    'n_estimators',
    'learning_rate',
    'num_leaves',
    'max_depth',
    'min_child_samples',
    'subsample',
    'colsample_bytree'
]

XGBOOST_HYPERPARAMETERS = [
    'n_estimators',
    'learning_rate',
    'max_depth',
    'subsample',
    'colsample_bytree',
    'gamma',
    'reg_alpha',
    'reg_lambda'
]

RIDGE_HYPERPARAMETERS = [
    'alpha',
    'fit_intercept',
    'solver',
    'positive'
]

# Model type to hyperparameters mapping
MODEL_HYPERPARAMETERS = {
    'lgbm': LGBM_HYPERPARAMETERS,
    'xgboost': XGBOOST_HYPERPARAMETERS,
    'xgb': XGBOOST_HYPERPARAMETERS,
    'ridge': RIDGE_HYPERPARAMETERS
}


def load_gridsearch_metadata(
    regression_model_type: str,
    metadata_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Load regression grid search metadata for a model type, merging input+working when available.

    This intentionally does not depend on any contest implementation modules.
    """
    input_dir = find_metadata_dir()
    working_dir = get_writable_metadata_dir()

    if metadata_dir is not None:
        working_dir = Path(metadata_dir)

    input_file = input_dir / regression_model_type / "gridsearch_metadata.json" if input_dir else None
    working_file = Path(working_dir) / regression_model_type / "gridsearch_metadata.json"

    merge_fn = lambda inp, wrk: merge_list_by_key_working_replaces(
        inp,
        wrk,
        key_fn=lambda r: (r.get("variant_id"), r.get("feature_filename")),
    )
    results = merge_json_from_input_and_working(
        input_file,
        working_file,
        merge_fn,
        expected_type=list,
        file_type="Regression gridsearch metadata JSON",
    )
    if not results:
        checked = [str(working_file)]
        if input_file is not None:
            checked.insert(0, str(input_file))
        files_str = "\n  ".join(checked)
        raise FileNotFoundError(
            "Grid search metadata not found in either location.\n"
            f"  Checked:\n  {files_str}\n"
            "Please run regression grid search first."
        )
    return results


def get_hyperparameters_for_model(model_type: str) -> List[str]:
    """
    Get list of hyperparameters for a given model type.
    
    Args:
        model_type: Type of model ('lgbm', 'xgboost', 'ridge')
        
    Returns:
        List of hyperparameter names for the model type
        
    Raises:
        ValueError: If model_type is not supported
    """
    model_type_lower = model_type.lower()
    if model_type_lower not in MODEL_HYPERPARAMETERS:
        raise ValueError(
            f"Unsupported model_type: {model_type}. "
            f"Must be one of: {list(MODEL_HYPERPARAMETERS.keys())}"
        )
    return MODEL_HYPERPARAMETERS[model_type_lower]


def normalize_hyperparameters(
    hyperparams: Dict[str, Any],
    model_type: str = 'lgbm'
) -> Tuple:
    """
    Normalize hyperparameters to a comparable signature.
    
    This matches the normalization used across tools for consistent comparison.
    
    Args:
        hyperparams: Dictionary of hyperparameters
        model_type: Type of model to determine parameter order ('lgbm', 'xgboost', 'ridge')
        
    Returns:
        Tuple of normalized values in consistent order
    """
    param_order = get_hyperparameters_for_model(model_type)
    
    normalized = []
    for param in param_order:
        value = hyperparams.get(param)
        if value is None:
            normalized.append(None)
        elif param in ['learning_rate', 'subsample', 'colsample_bytree', 'gamma', 'reg_alpha', 'reg_lambda']:
            # Round floats to 4 decimal places for consistent comparison
            normalized.append(round(float(value), 4))
        elif param in ['n_estimators', 'num_leaves', 'max_depth', 'min_child_samples', 'alpha']:
            # Convert to int (handles -1 for max_depth)
            try:
                normalized.append(int(value))
            except (ValueError, TypeError):
                # For very large alpha values, keep as float
                normalized.append(float(value))
        elif param in ['fit_intercept', 'positive']:
            # Boolean values
            normalized.append(bool(value))
        else:
            # String values (solver, etc.)
            normalized.append(str(value) if value is not None else None)
    
    return tuple(normalized)


def find_duplicates_in_metadata(
    metadata: List[Dict[str, Any]],
    model_type: str = 'lgbm'
) -> Dict[Tuple, List[Dict[str, Any]]]:
    """
    Find all duplicate hyperparameter combinations in metadata.
    
    Args:
        metadata: List of metadata entries with hyperparameters
        model_type: Type of model for normalization ('lgbm', 'xgboost', 'ridge')
        
    Returns:
        Dictionary mapping normalized signature to list of variant entries with that signature
    """
    signature_to_variants = defaultdict(list)
    
    for entry in metadata:
        hyperparams = entry.get('hyperparameters', {})
        if hyperparams:
            signature = normalize_hyperparameters(hyperparams, model_type=model_type)
            signature_to_variants[signature].append(entry)
    
    # Filter to only duplicates (more than one variant with same signature)
    duplicates = {
        sig: variants
        for sig, variants in signature_to_variants.items()
        if len(variants) > 1
    }
    
    return duplicates


def load_regression_metadata(
    regression_model_type: str,
    metadata_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Load regression metadata.json file.
    
    Reuses framework path resolution for consistency.
    
    Args:
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge')
        metadata_dir: Optional metadata directory (auto-detected if None)
        
    Returns:
        List of variant dictionaries from metadata.json
        
    Raises:
        FileNotFoundError: If metadata file not found
    """
    if metadata_dir is None:
        input_dir = find_metadata_dir()
        working_dir = get_writable_metadata_dir()
        
        if input_dir and str(input_dir).startswith('/kaggle/input'):
            metadata_dir = input_dir / regression_model_type
            if not (metadata_dir / 'metadata.json').exists():
                metadata_dir = working_dir / regression_model_type
        else:
            metadata_dir = working_dir / regression_model_type
    
    metadata_file = metadata_dir / 'metadata.json'
    
    if not metadata_file.exists():
        raise FileNotFoundError(
            f"Regression metadata file not found: {metadata_file}\n"
            f"Please ensure metadata.json exists for {regression_model_type}."
        )
    
    variants = load_json(metadata_file)
    logger.info(f"Loaded {len(variants)} variants from {metadata_file}")
    
    return variants


def load_and_join_metadata(
    regression_model_type: str,
    metadata_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Load both metadata.json and gridsearch_metadata.json and join by variant_id.
    
    Reuses framework functions: load_gridsearch_metadata() and load_regression_metadata()
    to follow DRY principles.
    
    Args:
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge')
        metadata_dir: Optional metadata directory (auto-detected if None)
        
    Returns:
        List of combined records with hyperparameters and scores
    """
    # Load metadata.json (hyperparameters)
    metadata = load_regression_metadata(regression_model_type, metadata_dir)
    
    # Load gridsearch_metadata.json (scores) - reuse framework function
    gridsearch_results = load_gridsearch_metadata(regression_model_type, metadata_dir)
    
    # Create lookup dictionaries
    metadata_dict = {item['variant_id']: item for item in metadata}
    gridsearch_dict = {item['variant_id']: item for item in gridsearch_results}
    
    # Join data
    combined = []
    for variant_id in set(list(metadata_dict.keys()) + list(gridsearch_dict.keys())):
        meta_item = metadata_dict.get(variant_id)
        grid_item = gridsearch_dict.get(variant_id)
        
        if meta_item and grid_item:
            combined.append({
                'variant_id': variant_id,
                'variant_index': meta_item.get('variant_index'),
                'hyperparameters': meta_item.get('hyperparameters', {}),
                'cv_score': grid_item.get('cv_score'),
                'fold_scores': grid_item.get('fold_scores', []),
                'feature_filename': grid_item.get('feature_filename')
            })
    
    logger.info(f"Joined {len(combined)} records from metadata and gridsearch_metadata")
    return combined


def extract_tested_values(
    metadata: List[Dict[str, Any]],
    model_type: str = 'lgbm'
) -> Dict[str, List[Any]]:
    """
    Extract all tested hyperparameter values from metadata.
    
    Args:
        metadata: List of metadata entries
        model_type: Type of model to determine which parameters to extract
        
    Returns:
        Dictionary mapping parameter names to sorted lists of tested values
    """
    param_names = get_hyperparameters_for_model(model_type)
    tested_values = defaultdict(set)
    
    for record in metadata:
        hyperparams = record.get('hyperparameters', {})
        for param in param_names:
            value = hyperparams.get(param)
            if value is not None:
                tested_values[param].add(value)
    
    # Convert sets to sorted lists
    return {k: sorted(list(v)) for k, v in tested_values.items()}


def generate_combinations(recommendations: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """
    Generate all hyperparameter combinations from recommendations.
    
    Args:
        recommendations: Dictionary mapping parameter names to lists of values
        
    Returns:
        List of all possible hyperparameter combination dictionaries
    """
    import itertools
    
    param_names = list(recommendations.keys())
    value_lists = [recommendations[param] for param in param_names]
    
    combinations = []
    for combo in itertools.product(*value_lists):
        combination_dict = dict(zip(param_names, combo))
        combinations.append(combination_dict)
    
    return combinations


def filter_out_existing_combinations(
    recommended_combos: List[Dict[str, Any]],
    metadata: List[Dict[str, Any]],
    model_type: str = 'lgbm'
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter out combinations that already exist in metadata.
    
    Args:
        recommended_combos: List of recommended hyperparameter combinations
        metadata: List of metadata entries with existing hyperparameters
        model_type: Type of model for normalization
        
    Returns:
        Tuple of (new_combinations, existing_combinations)
    """
    # Build set of existing signatures
    existing_signatures = set()
    existing_map = {}  # signature -> variant_id for reporting
    
    for entry in metadata:
        hyperparams = entry.get('hyperparameters', {})
        if hyperparams:
            signature = normalize_hyperparameters(hyperparams, model_type=model_type)
            existing_signatures.add(signature)
            if signature not in existing_map:
                existing_map[signature] = entry.get('variant_id')
    
    new_combos = []
    existing_combos = []
    
    for combo in recommended_combos:
        signature = normalize_hyperparameters(combo, model_type=model_type)
        if signature in existing_signatures:
            existing_combos.append({
                'combination': combo,
                'variant_id': existing_map.get(signature)
            })
        else:
            new_combos.append(combo)
    
    return new_combos, existing_combos
