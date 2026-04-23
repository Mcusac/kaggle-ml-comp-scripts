"""Model selection utilities for regression ensemble and stacking.
CSIRO-specific: uses csiro metadata paths and conventions."""

import json

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from layers.layer_0_core.level_0 import get_logger, is_kaggle_input

from layers.layer_0_core.level_5 import (
    merge_json_from_input_and_working,
    merge_list_by_key_working_replaces,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    find_metadata_dir,
    get_writable_metadata_dir,
)

_logger = get_logger(__name__)


def load_gridsearch_metadata(
    regression_model_type: str,
    metadata_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Load grid search metadata for a regression model type.

    Loads from both input and working directories, merging results.
    Working directory entries take precedence for duplicates.

    Args:
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge')
        metadata_dir: Optional metadata directory (auto-detected if None)

    Returns:
        List of variant result dictionaries from gridsearch_metadata.json
        (merged from input and working directories)

    Raises:
        FileNotFoundError: If metadata file not found in either location
    """
    input_dir = find_metadata_dir()
    working_dir = get_writable_metadata_dir()

    if input_dir and is_kaggle_input(input_dir):
        input_file = input_dir / regression_model_type / 'gridsearch_metadata.json'
        working_file = working_dir / regression_model_type / 'gridsearch_metadata.json'
    else:
        input_file = None
        working_file = working_dir / regression_model_type / 'gridsearch_metadata.json'

    merge_fn = lambda inp, wrk: merge_list_by_key_working_replaces(
        inp, wrk, key_fn=lambda r: (r.get("variant_id"), r.get("feature_filename"))
    )
    results = merge_json_from_input_and_working(
        input_file,
        working_file,
        merge_fn,
        expected_type=list,
        file_type="Regression gridsearch metadata JSON",
    )

    if not results:
        checked_files = []
        if input_file:
            checked_files.append(str(input_file))
        checked_files.append(str(working_file))
        files_str = "\n  ".join(checked_files)
        raise FileNotFoundError(
            f"Grid search metadata not found in either location.\n"
            f"  Checked:\n  {files_str}\n"
            f"Please run regression grid search (Cell 1c) first."
        )

    _logger.info(f"Loaded {len(results)} results (merged from input and working directories)")
    return results


def get_top_n_variants(
    regression_model_type: str,
    top_n: int,
    metadata_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Get top N variants from grid search results."""
    results = load_gridsearch_metadata(regression_model_type, metadata_dir)

    valid_results = [
        r for r in results
        if r.get('cv_score') is not None
        and not (isinstance(r.get('cv_score'), float) and (r['cv_score'] != r['cv_score']))
    ]

    if not valid_results:
        raise ValueError(f"No valid results found for {regression_model_type}")

    sorted_results = sorted(
        valid_results,
        key=lambda x: x.get('cv_score', -float('inf')),
        reverse=True
    )

    top_results = sorted_results[:top_n]

    _logger.info(
        f"Selected top {len(top_results)} {regression_model_type} variants "
        f"(from {len(valid_results)} valid)"
    )

    return top_results


def get_variant_info_from_model_id(
    regression_model_type: str,
    model_id: str,
    metadata_dir: Optional[Path] = None
) -> Tuple[str, str, Optional[float]]:
    """Get variant_id, feature_filename, and cv_score from model_id."""
    results = load_gridsearch_metadata(regression_model_type, metadata_dir)

    model_info = None
    for r in results:
        if r.get('model_id') == model_id:
            model_info = r
            break

    if model_info is None:
        available_ids = [r.get('model_id') for r in results if r.get('model_id')]
        raise ValueError(
            f"Model ID '{model_id}' not found in gridsearch_metadata.json for {regression_model_type}.\n"
            f"  Available model IDs (first 20): {sorted(set(available_ids))[:20]}..."
        )

    variant_id = model_info.get('variant_id')
    feature_filename = model_info.get('feature_filename')
    cv_score = model_info.get('cv_score')

    if not variant_id:
        raise ValueError(
            f"Model ID '{model_id}' has no variant_id in gridsearch_metadata.json. "
            f"This may indicate corrupted metadata."
        )

    if not feature_filename:
        raise ValueError(
            f"Model ID '{model_id}' has no feature_filename in gridsearch_metadata.json. "
            f"This may indicate corrupted metadata."
        )

    _logger.info(
        f"Looked up model_id '{model_id}' → variant_id {variant_id}, "
        f"feature_filename {feature_filename}, cv_score={cv_score}"
    )

    return variant_id, feature_filename, cv_score


def _resolve_auto_detected_models(
    model_types: List[str],
    model_versions: Dict[str, List[int]],
    base_model_dir: str
) -> Tuple[List[str], List[float], List[str]]:
    """Resolve model paths by auto-detecting from grid search metadata."""
    model_paths = []
    cv_scores = []
    resolved_model_types = []

    _logger.info("Auto-detecting top models from grid search metadata...")
    for model_type in model_types:
        if model_type not in model_versions:
            _logger.warning(f"No versions specified for {model_type}, skipping")
            continue

        versions = model_versions[model_type]
        if not versions:
            _logger.warning(f"Empty versions list for {model_type}, skipping")
            continue

        top_variants = get_top_n_variants(model_type, max(versions))

        for idx in versions:
            if idx < 1 or idx > len(top_variants):
                _logger.warning(
                    f"Index {idx} out of range for {model_type} "
                    f"(have {len(top_variants)} variants), skipping"
                )
                continue

            variant = top_variants[idx - 1]
            variant_id = variant.get('variant_id')

            if not variant_id:
                _logger.warning(f"Variant at index {idx} has no variant_id, skipping")
                continue

            model_path = Path(base_model_dir) / 'scikitlearn' / model_type / variant_id
            model_file = model_path / 'regression_model.pkl'

            if not model_file.exists():
                _logger.warning(f"Model not found: {model_file}, skipping")
                continue

            cv_score = variant.get('cv_score')
            model_paths.append(str(model_path))
            cv_scores.append(cv_score)
            resolved_model_types.append(model_type)

            cv_score_str = f"{cv_score:.6f}" if cv_score is not None else 'N/A'
            _logger.info(
                f"Auto-detected {model_type} variant {idx}: {variant_id} "
                f"(cv_score={cv_score_str})"
            )

    return model_paths, cv_scores, resolved_model_types


def _resolve_explicit_models(
    model_types: List[str],
    model_versions: Dict[str, List[int]],
    base_model_dir: str
) -> Tuple[List[str], List[float], List[str]]:
    """Resolve model paths from explicit version numbers in uploaded models."""
    model_paths = []
    cv_scores = []
    resolved_model_types = []

    _logger.info("Using explicit configuration (uploaded models by version)...")

    for model_type in model_types:
        if model_type not in model_versions:
            _logger.warning(f"No versions specified for {model_type}, skipping")
            continue

        versions = model_versions[model_type]
        if not versions:
            _logger.warning(f"Empty versions list for {model_type}, skipping")
            continue

        _logger.info(f"  {model_type}: model versions {versions} from /kaggle/input/csiro-models/scikitlearn/{model_type}/")

        for version in versions:
            model_path = Path(base_model_dir) / 'scikitlearn' / model_type / str(version)
            model_file = model_path / 'regression_model.pkl'
            metadata_file = model_path / 'model_metadata.json'

            if not model_file.exists():
                raise FileNotFoundError(
                    f"Uploaded model not found: {model_path}\n"
                    f"Expected path: /kaggle/input/csiro-models/scikitlearn/{model_type}/{version}/\n"
                    f"Please ensure model version {version} has been uploaded."
                )

            if not metadata_file.exists():
                _logger.warning(f"Metadata file not found: {metadata_file}, using default CV score")
                cv_score = None
            else:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                cv_score = metadata.get('cv_score')

            model_paths.append(str(model_path))
            cv_scores.append(cv_score)
            resolved_model_types.append(model_type)

            cv_score_str = f"{cv_score:.6f}" if cv_score is not None else 'N/A'
            _logger.info(
                f"  Resolved {model_type} version {version}: {model_path} "
                f"(cv_score={cv_score_str})"
            )

    return model_paths, cv_scores, resolved_model_types


def resolve_model_paths_from_config(
    ensemble_config: Dict[str, Any],
    base_model_dir: Optional[str] = None,
    auto_detect: bool = False
) -> Tuple[List[str], List[float], List[str]]:
    """Resolve model paths from ensemble configuration."""
    if base_model_dir is None:
        base_model_dir = '/kaggle/input/csiro-models/'

    model_types = ensemble_config.get('model_types', [])
    model_versions = ensemble_config.get('model_versions', {})

    if not model_types:
        raise ValueError("model_types cannot be empty in ensemble_config")

    if auto_detect:
        model_paths, cv_scores, resolved_model_types = _resolve_auto_detected_models(
            model_types, model_versions, base_model_dir
        )
    else:
        model_paths, cv_scores, resolved_model_types = _resolve_explicit_models(
            model_types, model_versions, base_model_dir
        )

    if not model_paths:
        raise ValueError(
            "No valid model paths resolved from configuration. "
            "Please check model_types and model_versions."
        )

    _logger.info(f"Resolved {len(model_paths)} model paths for ensemble")
    return model_paths, cv_scores, resolved_model_types


def validate_model_paths(
    model_paths: List[str],
    require_same_feature_model: bool = True
) -> None:
    """Validate that all model paths exist and are consistent."""
    feature_models = []

    for model_path in model_paths:
        model_path_obj = Path(model_path)

        model_file = model_path_obj / 'regression_model.pkl'
        if not model_file.exists():
            if model_path_obj.suffix == '.pkl' and model_path_obj.exists():
                model_file = model_path_obj
                model_path_obj = model_file.parent
            else:
                raise FileNotFoundError(f"Regression model not found: {model_path}")

        metadata_file = model_path_obj / 'model_metadata.json'
        if not metadata_file.exists():
            _logger.warning(f"Metadata file not found: {metadata_file}")
            continue

        if require_same_feature_model:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            feature_filename = metadata.get('feature_filename')
            if feature_filename:
                feature_models.append(feature_filename)

    if require_same_feature_model and feature_models:
        unique_features = set(feature_models)
        if len(unique_features) > 1:
            raise ValueError(
                f"Models use different feature extraction variants: {unique_features}\n"
                f"All models in ensemble must use the same feature extraction setup."
            )

    _logger.info(f"Validated {len(model_paths)} model paths")
