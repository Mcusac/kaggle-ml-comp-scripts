"""Utilities for finding and working with best variants from grid search results."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import find_best_fold_from_scores
from layers.layer_0_core.level_4 import load_json

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import find_metadata_dir, extract_preprocessing_augmentation_from_variant

logger = get_logger(__name__)


def load_results_json(results_file: Path) -> List[Dict]:
    """
    Load results from JSON file.

    Args:
        results_file: Path to results.json file

    Returns:
        List of variant result dictionaries
    """
    return load_json(results_file)


def find_best_variant(results: List[Dict]) -> Optional[Dict]:
    """
    Find the best variant from results based on highest cv_score.

    Only considers variants with valid cv_score (not None).

    Args:
        results: List of variant result dictionaries

    Returns:
        Best variant dictionary, or None if no valid variants found
    """
    valid_variants = [r for r in results if r.get('cv_score') is not None]

    if not valid_variants:
        logger.warning("No variants with valid cv_score found")
        return None

    best_variant = max(valid_variants, key=lambda x: x.get('cv_score', -float('inf')))

    return best_variant


def find_variant_by_id(results: List[Dict], variant_id: str) -> Optional[Dict]:
    """
    Find a specific variant by its variant_id.

    Args:
        results: List of variant result dictionaries
        variant_id: Variant ID to search for (e.g., "variant_0067")

    Returns:
        Variant dictionary if found, None otherwise
    """
    for result in results:
        if result.get('variant_id') == variant_id:
            return result

    return None


def get_variant_best_fold(variant: Dict) -> Tuple[int, float]:
    """
    Get the best fold for a variant from its fold_scores.

    Args:
        variant: Variant dictionary with 'fold_scores' key

    Returns:
        Tuple of (best_fold_index, best_fold_score)

    Raises:
        ValueError: If variant doesn't have fold_scores or fold_scores is empty
    """
    fold_scores = variant.get('fold_scores', [])

    if not fold_scores:
        raise ValueError(f"Variant {variant.get('variant_id', 'unknown')} has no fold_scores")

    return find_best_fold_from_scores(fold_scores)


def get_best_variant_info(
    results_file: Path,
    variant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about the best variant (or specified variant) from results.

    Args:
        results_file: Path to results.json file
        variant_id: Optional variant ID to use instead of finding best

    Returns:
        Dictionary with keys:
        - 'variant': Variant dictionary
        - 'best_fold': Best fold index
        - 'best_fold_score': Best fold score
        - 'preprocessing_list': List of preprocessing techniques
        - 'augmentation_list': List of augmentation techniques
        - 'cv_score': Cross-validation score
        - 'variant_id': Variant ID
        - 'dataset_type': Dataset type used

    Raises:
        FileNotFoundError: If results file doesn't exist
        ValueError: If variant not found or has no valid scores
    """
    results = load_results_json(results_file)

    if variant_id:
        variant = find_variant_by_id(results, variant_id)
        if variant is None:
            raise ValueError(f"Variant {variant_id} not found in results")
        if variant.get('cv_score') is None:
            raise ValueError(f"Variant {variant_id} has no valid cv_score (may have failed)")
    else:
        variant = find_best_variant(results)
        if variant is None:
            raise ValueError("No valid variants found in results")

    best_fold, best_fold_score = get_variant_best_fold(variant)

    # Resolve data_manipulation.combo_id to actual lists
    preprocessing_list = []
    augmentation_list = []

    try:
        metadata_dir = find_metadata_dir()
        if metadata_dir:
            preprocessing_list, augmentation_list = extract_preprocessing_augmentation_from_variant(
                variant, metadata_dir
            )
            logger.debug(f"Resolved variant {variant.get('variant_id', 'unknown')} to preprocessing={preprocessing_list}, augmentation={augmentation_list}")
        else:
            logger.warning(f"Metadata directory not found, cannot resolve combo_id for variant {variant.get('variant_id', 'unknown')}")
    except (ValueError, FileNotFoundError, ImportError) as e:
        logger.warning(f"Failed to resolve data_manipulation for variant {variant.get('variant_id', 'unknown')}: {e}")
        # Try to get from variant directly if available
        if 'preprocessing_list' in variant:
            preprocessing_list = variant.get('preprocessing_list', [])
        if 'augmentation_list' in variant:
            augmentation_list = variant.get('augmentation_list', [])

    return {
        'variant': variant,
        'best_fold': best_fold,
        'best_fold_score': best_fold_score,
        'preprocessing_list': preprocessing_list,
        'augmentation_list': augmentation_list,
        'cv_score': variant.get('cv_score'),
        'variant_id': variant.get('variant_id'),
        'dataset_type': variant.get('dataset_type', 'split')
    }
