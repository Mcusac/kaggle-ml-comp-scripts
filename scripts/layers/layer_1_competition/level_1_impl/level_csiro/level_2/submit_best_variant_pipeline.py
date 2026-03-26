"""Submit best variant pipeline for CSIRO contest."""

from pathlib import Path
from typing import Optional, Any

from layers.layer_0_core.level_0 import get_fold_checkpoint_path, get_logger

from layers.layer_1_competition.level_0_infra.level_1 import build_contest_context, get_contest

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    apply_combo_to_config,
    get_best_variant_info,
    test_pipeline,
)

logger = get_logger(__name__)


def submit_best_variant_pipeline(
    data_root: Optional[str] = None,
    variant_id: Optional[str] = None,
    results_file: Optional[str] = None,
    **kwargs
) -> None:
    """
    Generate submission using the best variant from grid search.
    """
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()

    data_root = data_root or str(paths.get_data_root())
    results_path = _resolve_results_file_path(results_file, paths)

    variant_info = _load_variant_info(results_path, variant_id)
    _log_variant_info(variant_info)

    model_path = _find_variant_model_path(paths, variant_info)
    logger.info(f"Using model checkpoint: {model_path}")

    _apply_variant_config(config, variant_info)

    logger.info("Generating submission...")
    contest_context = build_contest_context("csiro")
    test_pipeline(
        contest_context=contest_context,
        data_root=data_root,
        model_path=str(model_path),
        **kwargs
    )

    _log_submission_success(variant_info)


def _resolve_results_file_path(results_file: Optional[str], paths: Any) -> Path:
    """Resolve results file path."""
    if results_file is None:
        results_file = str(paths.get_output_dir() / 'dataset_grid_search' / 'gridsearch_results.json')
    return Path(results_file)


def _load_variant_info(results_path: Path, variant_id: Optional[str]) -> dict:
    """Load variant information from results file."""
    logger.info(f"Loading variant information from: {results_path}")
    try:
        return get_best_variant_info(results_path, variant_id=variant_id)
    except Exception as e:
        logger.error(f"Failed to load variant information: {e}")
        raise


def _log_variant_info(variant_info: dict) -> None:
    """Log variant information."""
    variant_id = variant_info['variant_id']
    cv_score = variant_info['cv_score']
    best_fold = variant_info['best_fold']
    best_fold_score = variant_info['best_fold_score']
    preprocessing_list = variant_info['preprocessing_list']
    augmentation_list = variant_info['augmentation_list']

    logger.info("=" * 60)
    logger.info(f"Using variant: {variant_id}")
    logger.info(f"  CV Score: {cv_score:.4f}")
    logger.info(f"  Best Fold: {best_fold} (score: {best_fold_score:.4f})")
    logger.info(f"  Preprocessing: {preprocessing_list if preprocessing_list else '[]'}")
    logger.info(f"  Augmentation: {augmentation_list if augmentation_list else '[]'}")
    logger.info("=" * 60)


def _find_variant_model_path(paths: Any, variant_info: dict) -> Path:
    """Find model checkpoint path for variant."""
    model_dir = paths.get_models_base_dir()
    variant_id = variant_info['variant_id']
    best_fold = variant_info['best_fold']

    variant_model_dir = model_dir / 'dataset_grid_search' / variant_id
    model_path = get_fold_checkpoint_path(variant_model_dir, best_fold)

    if not model_path.exists():
        model_path = model_dir / variant_id / f'fold_{best_fold}' / 'best_model.pth'
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found for variant {variant_id}, fold {best_fold}. "
                f"Tried: {variant_model_dir / f'fold_{best_fold}' / 'best_model.pth'} and {model_path}"
            )

    return model_path


def _apply_variant_config(config: Any, variant_info: dict) -> None:
    """Apply preprocessing and augmentation to config."""
    preprocessing_list = variant_info['preprocessing_list']
    augmentation_list = variant_info['augmentation_list']

    if not (preprocessing_list or augmentation_list):
        return

    logger.info("Applying preprocessing and augmentation configuration...")
    variant = variant_info['variant']
    combo_id = variant.get('combo_id')

    if combo_id:
        try:
            apply_combo_to_config(config, combo_id)
            return
        except Exception:
            pass

    if hasattr(config, 'data'):
        if preprocessing_list:
            config.data.preprocessing_list = preprocessing_list
        if augmentation_list:
            config.data.augmentation_list = augmentation_list


def _log_submission_success(variant_info: dict) -> None:
    """Log submission success message."""
    variant_id = variant_info['variant_id']
    cv_score = variant_info['cv_score']
    best_fold = variant_info['best_fold']
    best_fold_score = variant_info['best_fold_score']

    logger.info("=" * 60)
    logger.info("✅ Submission generated successfully!")
    logger.info(f"  Variant: {variant_id}")
    logger.info(f"  CV Score: {cv_score:.4f}")
    logger.info(f"  Best Fold: {best_fold} (score: {best_fold_score:.4f})")
    logger.info("=" * 60)
