"""Submit lightweight pipeline (Pipeline A). Requires contest_context from contest layer."""

from pathlib import Path
from typing import Optional, Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import resolve_environment_path, find_metadata_candidates, get_device
from layers.layer_0_core.level_2 import resolve_extraction_info
from layers.layer_0_core.level_4 import load_json
from layers.layer_0_core.level_5 import find_trained_model_path

from layers.layer_1_competition.level_0_infra.level_0 import load_feature_filename_from_gridsearch
from layers.layer_1_competition.level_0_infra.level_6 import create_regression_submission

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    apply_combo_to_config,
    find_best_variant,
)

_logger = get_logger(__name__)


def _find_model_path(
    model_path: Optional[str],
    paths: Any
) -> Path:
    """
    Find model checkpoint path, handling both files and directories.

    If model_path is a directory, looks for regression_model.pkl or best_model.pth inside it.
    This matches the pattern from csiro-scripts LightweightSubmissionModelFinder.

    Args:
        model_path: Optional explicit model path (can be file or directory)
        paths: Contest paths object

    Returns:
        Model path (always a file, never a directory)

    Raises:
        FileNotFoundError: If model not found
    """
    if model_path:
        found_path = Path(model_path)
        if not found_path.exists():
            raise FileNotFoundError(f"Model path not found: {found_path}")

        # If directory, look for model file inside
        if found_path.is_dir():
            regression_model = found_path / 'regression_model.pkl'
            best_model = found_path / 'best_model.pth'

            if regression_model.exists():
                _logger.info(f"Found regression model in directory: {regression_model}")
                return regression_model
            elif best_model.exists():
                _logger.info(f"Found end-to-end model in directory: {best_model}")
                return best_model
            else:
                # Look for any .pkl or .pth files
                pkl_files = list(found_path.glob('*.pkl'))
                if pkl_files:
                    _logger.info(f"Found .pkl file in directory: {pkl_files[0]}")
                    return pkl_files[0]
                pth_files = list(found_path.glob('*.pth'))
                if pth_files:
                    _logger.info(f"Found .pth file in directory: {pth_files[0]}")
                    return pth_files[0]
                raise FileNotFoundError(
                    f"Model path is a directory but no checkpoint found: {found_path}\n"
                    f"Expected: regression_model.pkl or best_model.pth\n"
                    f"Directory contents: {list(found_path.iterdir())}"
                )

        # Path is a file
        return found_path

    # Try to find model in standard locations
    models_dir = paths.get_models_base_dir()
    if models_dir.exists():
        try:
            found_path, _ = find_trained_model_path(models_dir)
            return found_path
        except FileNotFoundError:
            pass

    raise FileNotFoundError("Could not find model checkpoint. Please provide model_path.")


def _load_metadata(
    metadata_path: Optional[str],
    model_path: Path,
    results_file: Optional[str],
    dataset_type: str,
    contest_context: Any = None
) -> dict:
    """
    Load metadata from file or extract from results.json.

    Args:
        metadata_path: Optional explicit metadata path
        model_path: Model path (for searching nearby). Can be a file or directory.
        results_file: Optional results.json path (fallback)
        dataset_type: Default dataset type
        contest_context: Optional; if provided with load_regression_gridsearch_results, used for gridsearch fallback

    Returns:
        Metadata dictionary
    """
    # Try explicit path first
    if metadata_path:
        found_path = Path(metadata_path)
        if found_path.exists():
            return load_json(found_path)

    # Try to find metadata next to model
    metadata_candidates = find_metadata_candidates(model_path)

    for candidate in metadata_candidates:
        if candidate.exists():
            metadata = load_json(candidate)

            # For regression models, ensure feature_filename is present
            # If missing, try fallback to grid search metadata (when contest_context provides loader)
            if metadata.get('regression_model_type') and not metadata.get('feature_filename'):
                variant_id = metadata.get('variant_id')
                regression_model_type = metadata.get('regression_model_type')
                load_feature_filename_from_gridsearch(
                    variant_id, regression_model_type, metadata, contest_context=contest_context
                )

            return metadata

    # Fallback to results.json
    if results_file and Path(results_file).exists():
        results = load_json(Path(results_file))
        if results and len(results) > 0:
            best_variant = find_best_variant(results)
            if best_variant:
                return {
                    'preprocessing_list': best_variant.get('preprocessing_list', []),
                    'augmentation_list': best_variant.get('augmentation_list', []),
                    'best_fold': best_variant.get('best_fold', 0),
                    'dataset_type': best_variant.get('dataset_type', dataset_type)
                }

    return {}


def _apply_metadata_to_config(
    config: Any,
    metadata: dict
) -> None:
    """
    Apply preprocessing and augmentation from metadata to config.

    Args:
        config: Configuration object
        metadata: Metadata dictionary
    """
    preprocessing_list = metadata.get('preprocessing_list', [])
    augmentation_list = metadata.get('augmentation_list', [])

    if not (preprocessing_list or augmentation_list):
        return


    # Try to apply via combo_id if available
    combo_id = metadata.get('combo_id')
    if combo_id:
        try:
            apply_combo_to_config(config, combo_id)
            return
        except Exception:
            pass

    # Fallback: apply directly
    if hasattr(config, 'data'):
        if preprocessing_list:
            config.data.preprocessing_list = preprocessing_list
        if augmentation_list:
            config.data.augmentation_list = augmentation_list


def _generate_regression_submission(
    model_path: Path,
    metadata: dict,
    data_root: str,
    config: Any,
    paths: Any,
    contest_context: Any,
) -> None:
    """
    Generate submission using regression model.

    Args:
        model_path: Model path
        metadata: Metadata dictionary
        data_root: Data root directory
        config: Contest configuration object
        paths: Contest paths object

    Raises:
        ValueError: If feature_filename not in metadata
    """
    _logger.info("Generating submission using regression model...")
    feature_filename = metadata.get('feature_filename')

    if not feature_filename:
        # Provide helpful error message
        model_dir = model_path.parent if model_path.is_file() else model_path
        metadata_file = model_dir / 'model_metadata.json'
        raise ValueError(
            f"feature_filename required for regression model submission.\n"
            f"Model path: {model_path}\n"
            f"Expected metadata file: {metadata_file}\n"
            f"Metadata file exists: {metadata_file.exists()}\n"
            f"Metadata keys found: {list(metadata.keys())}\n"
            f"Please ensure the model was exported with complete metadata including feature_filename."
        )

    # Parse feature_filename to get feature extraction model and data manipulation info
    # This follows the pattern from csiro-scripts submit_lightweight.py
    try:
        extraction_info = resolve_extraction_info(feature_filename)
        feature_extraction_model_name = extraction_info['model_name']
        preprocessing_list = extraction_info['preprocessing_list']
        augmentation_list = extraction_info['augmentation_list']

        _logger.info(f"Parsed feature_filename '{feature_filename}':")
        _logger.info(f"  Feature extraction model: {feature_extraction_model_name}")
        _logger.info(f"  Data manipulation combo: {extraction_info['combo_id']}")
        _logger.info(f"  Preprocessing: {preprocessing_list if preprocessing_list else '[]'}")
        _logger.info(f"  Augmentation: {augmentation_list if augmentation_list else '[]'}")
    except Exception as e:
        raise ValueError(
            f"Failed to parse feature_filename '{feature_filename}': {e}. "
            f"Please ensure the feature_filename is valid (e.g., 'variant_0100_features.npz')."
        )

    # Set dataset_type to 'split' (default for regression - feature extraction handles splitting)
    dataset_type = 'split'
    if hasattr(config, 'data'):
        config.data.dataset_type = dataset_type
    _logger.info(f"Using dataset_type: 'split' (default for regression models)")

    # Apply preprocessing and augmentation to config (from feature extraction)
    # This is CRITICAL - must match what was used during feature extraction
    if preprocessing_list or augmentation_list:
        _logger.info("Applying preprocessing and augmentation configuration from feature extraction...")
        combo_id = extraction_info.get('combo_id')
        if combo_id:
            try:
                apply_combo_to_config(config, combo_id)
            except Exception:
                # Fallback: apply directly
                if hasattr(config, 'data'):
                    if preprocessing_list:
                        config.data.preprocessing_list = preprocessing_list
                    if augmentation_list:
                        config.data.augmentation_list = augmentation_list
        else:
            # Apply directly if no combo_id
            if hasattr(config, 'data'):
                if preprocessing_list:
                    config.data.preprocessing_list = preprocessing_list
                if augmentation_list:
                    config.data.augmentation_list = augmentation_list

    device = get_device('auto')
    test_csv_path = Path(data_root) / 'test.csv'
    output_path = resolve_environment_path('submission.csv', purpose='output')
    data_schema = contest_context.get_data_schema()
    post_processor = contest_context.get_post_processor()

    create_regression_submission(
        regression_model_path=str(model_path),
        feature_extraction_model_name=feature_extraction_model_name,
        test_csv_path=str(test_csv_path),
        data_root=data_root,
        config=config,
        device=device,
        output_path=str(output_path),
        data_schema=data_schema,
        post_processor=post_processor,
    )


def submit_lightweight_pipeline(
    contest_context: Any,
    data_root: Optional[str] = None,
    model_path: Optional[str] = None,
    metadata_path: Optional[str] = None,
    results_file: Optional[str] = None,
    model_name: Optional[str] = None,
    dataset_type: str = 'split',
    **kwargs
) -> None:
    """
    Lightweight submission pipeline. Contest passes contest_context.
    """
    paths = contest_context.get_paths()
    config = contest_context.get_config()

    # Resolve data root
    if data_root is None:
        data_root = str(paths.get_data_root())

    # Find model
    found_model_path = _find_model_path(model_path, paths)

    # Load metadata
    metadata = _load_metadata(
        metadata_path, found_model_path, results_file, dataset_type,
        contest_context=contest_context
    )

    # Apply metadata to config
    _apply_metadata_to_config(config, metadata)

    # Set dataset type
    dataset_type_from_metadata = metadata.get('dataset_type', dataset_type)
    if hasattr(config, 'data'):
        config.data.dataset_type = dataset_type_from_metadata

    # Determine if this is a regression model
    # _find_model_path now always returns a file path (handles directories internally)
    is_regression_model = found_model_path.suffix == '.pkl'

    # Also check metadata if available (fallback detection)
    if not is_regression_model and metadata:
        model_type = metadata.get('model_type')
        regression_model_type = metadata.get('regression_model_type')
        if model_type == 'regression' or regression_model_type:
            is_regression_model = True

    # Generate submission
    if is_regression_model:
        _generate_regression_submission(
            found_model_path, metadata, data_root, config, paths, contest_context
        )
    else:
        _logger.info("Generating submission using end-to-end model...")
        test_pipeline_fn = contest_context.get_test_pipeline()
        test_pipeline_fn(
            contest_context=contest_context,
            data_root=data_root,
            model_path=str(found_model_path),
            dataset_type=dataset_type_from_metadata,
            **kwargs
        )

    _logger.info("=" * 60)
    _logger.info("✅ Submission generated successfully!")
    _logger.info(f"  Model: {found_model_path}")
    _logger.info(f"  Dataset Type: {dataset_type_from_metadata}")
    _logger.info("=" * 60)
