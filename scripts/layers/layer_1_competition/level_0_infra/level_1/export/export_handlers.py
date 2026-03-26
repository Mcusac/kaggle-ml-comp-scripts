"""Export handlers for different scenarios"""

import json

from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from layers.layer_0_core.level_0 import ConfigValidationError, get_logger
from layers.layer_0_core.level_1 import generate_feature_filename
from layers.layer_0_core.level_5 import find_metadata_dir, find_trained_model_path

from layers.layer_1_competition.level_0_infra.level_0 import get_model_id, get_model_name_from_pretrained

logger = get_logger(__name__)


def prepare_regression_model_metadata_dict(
    regression_model_type: str,
    cv_score: float,
    fold_scores: list[float],
    hyperparameters: Dict[str, Any],
    feature_filename: str,
    variant_id: str,
    variant_index: int,
    best_fold: Optional[int] = None,
    best_fold_score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create regression model metadata dictionary from explicit parameters.

    Regression models train on pre-extracted features. The feature filename
    identifies which feature file was used for training.

    Args:
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge')
        cv_score: Cross-validation score
        fold_scores: List of scores for each fold
        hyperparameters: Model-specific hyperparameters dictionary
        feature_filename: Feature filename used for training (e.g., 'variant_0100_features.npz')
        variant_id: Variant ID (e.g., 'variant_0000')
        variant_index: Sequential variant index (e.g., 0, 1, 2)
        best_fold: Optional best fold number
        best_fold_score: Optional best fold score

    Returns:
        Dictionary with regression model metadata
    """
    metadata = {
        'regression_model_type': regression_model_type,
        'variant_index': variant_index,
        'variant_id': variant_id,
        'cv_score': cv_score,
        'fold_scores': fold_scores,
        'hyperparameters': hyperparameters,
        'feature_filename': feature_filename
    }

    # Add optional fields if provided
    if best_fold is not None:
        metadata['best_fold'] = best_fold
    if best_fold_score is not None:
        metadata['best_fold_score'] = best_fold_score

    return metadata


def _extract_scores_from_json(
    model_path: Path,
    json_filename: str,
    best_fold: Optional[int],
) -> tuple[float, list, Optional[int]]:
    """
    Extract CV scores and fold scores from a JSON metadata file in the model's fold directory.

    Args:
        model_path: Path to model file (parent dir contains the JSON)
        json_filename: Name of JSON file (e.g., 'regression_model_info.json', 'checkpoint_metadata.json')
        best_fold: Best fold from model finding (fallback if not in JSON)

    Returns:
        Tuple of (cv_score, fold_scores, extracted_best_fold)
    """
    metadata_path = model_path.parent / json_filename
    cv_score = 0.0
    fold_scores = []
    extracted_best_fold = best_fold

    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                info = json.load(f)
                cv_score = info.get('cv_score', 0.0)
                fold_scores = info.get('fold_scores', [])
                extracted_best_fold = info.get('best_fold', best_fold)
        except Exception as e:
            logger.warning(f"Could not load {json_filename}: {e}")

    return cv_score, fold_scores, extracted_best_fold


def _resolve_best_fold_and_score(
    best_fold: Optional[int],
    extracted_best_fold: Optional[int],
    fold_scores: list,
    cv_score: float,
) -> tuple[Optional[int], float]:
    """Resolve best fold index and its score from fold_scores or cv_score fallback."""
    best_fold_used = best_fold if best_fold is not None else extracted_best_fold
    best_fold_score = (
        fold_scores[best_fold_used] if best_fold_used is not None and best_fold_used < len(fold_scores)
        else cv_score
    )
    return best_fold_used, best_fold_score


def _construct_feature_filename_from_config(config: Any) -> Optional[str]:
    """
    Construct feature filename from config settings.

    Args:
        config: Configuration object

    Returns:
        Feature filename if constructed, None otherwise
    """
    if not getattr(config.model, 'feature_extraction_mode', False):
        return None

    try:
        # Resolve model name
        model_name = _resolve_feature_extraction_model_name(config)
        if not model_name:
            return None

        # Find combo ID
        combo_id = _find_combo_id_from_config(config)
        if not combo_id:
            return None

        # Generate feature filename
        model_id = get_model_id(model_name)
        feature_filename = generate_feature_filename(model_id, combo_id)
        logger.info(f"Constructed feature_filename from config: {feature_filename}")
        return feature_filename
    except Exception as e:
        logger.warning(f"Could not construct feature_filename from config: {e}")
        return None


def _resolve_feature_extraction_model_name(config: Any) -> Optional[str]:
    """Resolve feature extraction model name from config."""
    feature_extraction_model_name = getattr(config.model, 'feature_extraction_model_name', None)
    if not feature_extraction_model_name:
        return None

    # Convert path to model name if needed
    if '/' in feature_extraction_model_name or feature_extraction_model_name.startswith('/'):
        resolved_name = get_model_name_from_pretrained(feature_extraction_model_name)
        if resolved_name:
            return resolved_name

    return feature_extraction_model_name


def _find_combo_id_from_config(config: Any) -> Optional[str]:
    """Find combo ID from config preprocessing/augmentation settings."""
    try:
        preprocessing_list = getattr(config.data, 'preprocessing_list', []) or []
        augmentation_list = getattr(config.data, 'augmentation_list', []) or []

        metadata_dir = find_metadata_dir()
        if not metadata_dir:
            return None

        combo_metadata_path = metadata_dir / 'data_manipulation' / 'metadata.json'
        if not combo_metadata_path.exists():
            return None

        with open(combo_metadata_path, 'r') as f:
            combos_list = json.load(f)

        # Find combo by preprocessing/augmentation
        for combo in combos_list:
            if (combo.get('preprocessing_list') == preprocessing_list and
                combo.get('augmentation_list') == augmentation_list):
                return combo.get('combo_id')

        return None
    except Exception as e:
        logger.warning(f"Could not find combo_id: {e}")
        return None


def _build_regression_metadata(
    config: Any,
    model_path: Path,
    best_fold: Optional[int],
    variant_id: Optional[str],
    variant_info: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build regression model metadata.

    Args:
        config: Configuration object
        model_path: Path to model
        best_fold: Best fold number
        variant_id: Optional variant ID
        variant_info: Optional variant info

    Returns:
        Metadata dictionary

    Raises:
        ValueError: If required fields missing
    """
    regression_model_type = getattr(config.model, 'regression_model_type', None)
    if not regression_model_type:
        raise ConfigValidationError("regression_model_type must be set in config for regression model export")

    # Extract scores
    cv_score, fold_scores, extracted_best_fold = _extract_scores_from_json(
        model_path, 'regression_model_info.json', best_fold
    )
    best_fold_used, best_fold_score = _resolve_best_fold_and_score(
        best_fold, extracted_best_fold, fold_scores, cv_score
    )

    # Get feature filename
    feature_filename = None
    if variant_info:
        feature_filename = variant_info.get('feature_filename')

    if not feature_filename:
        feature_filename = _construct_feature_filename_from_config(config)

    if not feature_filename:
        raise ValueError(
            "feature_filename is required for regression model export. "
            "Provide it in variant_info or ensure config has feature_extraction_model_name and data manipulation settings."
        )

    # Extract other fields
    hyperparameters = variant_info.get('hyperparameters', {}) if variant_info else {}
    variant_id_used = variant_id or (variant_info.get('variant_id') if variant_info else None)
    variant_index_used = variant_info.get('variant_index') if variant_info else 0

    if not variant_id_used:
        raise ValueError("variant_id is required for regression model export. Provide it in variant_info or as parameter.")

    # Build metadata
    metadata = prepare_regression_model_metadata_dict(
        regression_model_type=regression_model_type,
        cv_score=cv_score,
        fold_scores=fold_scores,
        hyperparameters=hyperparameters,
        feature_filename=feature_filename,
        variant_id=variant_id_used,
        variant_index=variant_index_used,
        best_fold=best_fold_used,
        best_fold_score=best_fold_score
    )

    logger.info(f"Built regression model metadata: regression_model_type={regression_model_type}, feature_filename={feature_filename}")
    return metadata




def _build_end_to_end_metadata(
    config: Any,
    model_path: Path,
    best_fold: Optional[int],
    variant_id: Optional[str],
    variant_info: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build end-to-end model metadata.

    Args:
        config: Configuration object
        model_path: Path to model
        best_fold: Best fold number
        variant_id: Optional variant ID
        variant_info: Optional variant info

    Returns:
        Metadata dictionary
    """
    model_name = getattr(config.model, 'name', 'unknown')
    preprocessing_list = getattr(config.data, 'preprocessing_list', []) or []
    augmentation_list = getattr(config.data, 'augmentation_list', []) or []

    # Extract scores
    cv_score, fold_scores, extracted_best_fold = _extract_scores_from_json(
        model_path, 'checkpoint_metadata.json', best_fold
    )
    best_fold_used, best_fold_score = _resolve_best_fold_and_score(
        best_fold, extracted_best_fold, fold_scores, cv_score
    )

    metadata = {
        'model_name': model_name,
        'preprocessing_list': preprocessing_list,
        'augmentation_list': augmentation_list,
        'cv_score': cv_score,
        'fold_scores': fold_scores,
        'best_fold': best_fold_used,
        'best_fold_score': best_fold_score,
        'dataset_type': getattr(config.data, 'dataset_type', 'split')
    }

    if variant_id:
        metadata['variant_id'] = variant_id
    if variant_info:
        for key in ['variant_index', 'feature_filename']:
            if key in variant_info:
                metadata[key] = variant_info[key]

    return metadata


def handle_just_trained_model(
    model_dir: str,
    config: Any,
    variant_id: Optional[str] = None,
    variant_info: Optional[Dict[str, Any]] = None
) -> Tuple[Path, Dict[str, Any]]:
    """
    Handle export from just-trained model directory.

    Args:
        model_dir: Path to just-trained model directory
        config: Configuration object (must have model.regression_model_type if regression model)
        variant_id: Optional variant ID
        variant_info: Optional variant info dictionary from training

    Returns:
        Tuple of (model_path, metadata_dict)

    Raises:
        FileNotFoundError: If model directory not found
        ValueError: If required fields missing
    """
    model_dir_path = Path(model_dir)
    if not model_dir_path.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir_path}")

    # Find model checkpoint
    model_path, best_fold = find_trained_model_path(model_dir_path)

    # Build metadata based on model type
    if model_path.suffix == '.pkl':
        metadata = _build_regression_metadata(config, model_path, best_fold, variant_id, variant_info)
    else:
        metadata = _build_end_to_end_metadata(config, model_path, best_fold, variant_id, variant_info)

    return model_path, metadata


def handle_best_variant_file(
    best_variant_file: str,
    config: Any,
    export_dir: Optional[str] = None,
    paths: Optional[Any] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Read best variant pointer file, locate model directory, export via handle_just_trained_model.

    Expects JSON with 'model_dir' or 'variant_id'. If variant_id, uses paths to construct model_dir.
    """
    path = Path(best_variant_file)
    if not path.exists():
        raise FileNotFoundError(f"Best variant file not found: {path}")

    with open(path, 'r') as f:
        data = json.load(f)

    model_dir = data.get('model_dir')
    if not model_dir and data.get('variant_id') and paths:
        model_dir = str(paths.get_models_base_dir() / 'dataset_grid_search' / data['variant_id'])
    if not model_dir:
        raise ValueError("Best variant file must contain 'model_dir' or 'variant_id' (with paths)")

    return handle_just_trained_model(model_dir=model_dir, config=config)


def handle_results_file(
    results_file: str,
    variant_id: str,
    config: Any,
    export_dir: Optional[str] = None,
    paths: Optional[Any] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Read results file, find variant by variant_id, locate model directory, export.
    """
    path = Path(results_file)
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")

    if path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            raw = json.load(f)
    else:
        results = _parse_results_csv(path)
        raw = None

    if raw is not None:
        if isinstance(raw, list):
            results = raw
        elif isinstance(raw, dict) and 'results' in raw:
            results = raw['results']
        else:
            results = [raw] if isinstance(raw, dict) else []

    variant = None
    for r in results:
        if isinstance(r, dict) and r.get('variant_id') == variant_id:
            variant = r
            break

    if not variant:
        raise ValueError(f"Variant {variant_id} not found in results file")

    model_dir = variant.get('model_dir') or variant.get('model_path')
    if not model_dir and paths:
        model_dir = str(paths.get_models_base_dir() / 'dataset_grid_search' / variant_id)
    if not model_dir:
        raise ValueError(f"Cannot resolve model_dir for variant {variant_id}")

    return handle_just_trained_model(
        model_dir=model_dir,
        config=config,
        variant_id=variant_id,
        variant_info=variant if isinstance(variant, dict) else None,
    )


def _parse_results_csv(path: Path) -> list:
    """Parse CSV results file; return list of dicts with variant_id and model_dir if present."""
    import csv
    rows = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip() if isinstance(k, str) else k: v for k, v in row.items()})
    return rows


def handle_auto_detect(
    model_dir: str,
    config: Any,
    export_dir: Optional[str] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Scan model_dir for best model, export via handle_just_trained_model.
    """
    return handle_just_trained_model(model_dir=model_dir, config=config)
