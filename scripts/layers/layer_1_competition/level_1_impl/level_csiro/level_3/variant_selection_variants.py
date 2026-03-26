"""Resolve regression variant IDs, load variant records, persist gridsearch results."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger, is_kaggle_input
from layers.layer_0_core.level_4 import load_json, save_json
from layers.layer_0_core.level_5 import merge_json_from_input_and_working, merge_list_by_key_add_only

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    find_metadata_dir,
    get_writable_metadata_dir,
    validate_regression_model_type,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    load_gridsearch_metadata,    
    find_variant_by_id,
    hyperparameters_signature,
    load_and_merge_variants,
    load_gridsearch_scores,
    resolve_metadata_file_locations,
    to_jsonable,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import (
    initialize_working_metadata_files,
)

logger = get_logger(__name__)


def find_best_regression_variant(
    regression_model_type: str,
    feature_filename: Optional[str] = None,
    metadata_dir: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Find the best regression variant (highest CV score) from grid search results.

    Filters by feature_filename if provided, then selects variant with highest cv_score.
    Only considers variants with valid cv_score (not None).
    """
    results = load_gridsearch_metadata(regression_model_type, metadata_dir)

    if feature_filename:
        results = [r for r in results if r.get("feature_filename") == feature_filename]

    valid_variants = [r for r in results if r.get("cv_score") is not None]

    if not valid_variants:
        logger.warning("No variants with valid cv_score found for %s", regression_model_type)
        if feature_filename:
            logger.warning("  Filtered by feature_filename: %s", feature_filename)
        return None

    best_variant = max(valid_variants, key=lambda x: x.get("cv_score", -float("inf")))

    cv_score = best_variant.get("cv_score")
    logger.info(
        "Found best regression variant: %s (CV score: %.4f)",
        best_variant.get("variant_id"),
        cv_score,
    )

    return best_variant


def get_or_create_regression_variant_id(
    regression_model_type: str,
    hyperparameters: Dict[str, Any],
) -> Tuple[str, int]:
    """
    Resolve hyperparameters to an existing regression variant_id, or append a new variant.

    The source of truth for variant definitions is `metadata.json`. If the hyperparameters
    are not present in either input or working metadata, a new variant is appended to the
    working `metadata.json` with the next sequential variant_index.

    Returns:
        (variant_id, variant_index)
    """
    working_metadata_file, _ = initialize_working_metadata_files(regression_model_type)

    input_file, _ = resolve_metadata_file_locations(regression_model_type)
    merged_variants = load_and_merge_variants(input_file, working_metadata_file)

    target_sig = hyperparameters_signature(hyperparameters)

    best_match: Optional[Tuple[str, int]] = None
    for v in merged_variants:
        hp = v.get("hyperparameters") or {}
        if not isinstance(hp, dict):
            continue
        if hyperparameters_signature(hp) != target_sig:
            continue
        variant_id = v.get("variant_id")
        variant_index = v.get("variant_index")
        if isinstance(variant_id, str) and isinstance(variant_index, int):
            if best_match is None or variant_index < best_match[1]:
                best_match = (variant_id, variant_index)

    if best_match is not None:
        return best_match

    try:
        working_variants = load_json(
            working_metadata_file, expected_type=list, file_type="Regression metadata JSON"
        )
    except Exception:
        working_variants = []

    max_idx = -1
    for v in merged_variants:
        idx = v.get("variant_index")
        if isinstance(idx, int) and idx > max_idx:
            max_idx = idx
    next_index = max_idx + 1
    new_variant_id = f"variant_{next_index:04d}"

    new_entry = {
        "variant_index": next_index,
        "variant_id": new_variant_id,
        "hyperparameters": to_jsonable(hyperparameters),
    }
    working_variants.append(new_entry)
    save_json(working_variants, working_metadata_file)
    logger.info(
        "Added new regression variant to working metadata.json: %s (variant_index=%s)",
        new_variant_id,
        next_index,
    )

    return new_variant_id, next_index


def load_regression_variant_from_metadata(
    regression_model_type: str,
    variant_id: str,
    feature_filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load regression model variant from metadata file.

    Loads hyperparameters from metadata.json. Optionally loads CV scores from
    gridsearch_metadata.json if feature_filename is provided.
    """
    validate_regression_model_type(regression_model_type)

    input_file, working_file = resolve_metadata_file_locations(regression_model_type)

    variants = load_and_merge_variants(input_file, working_file)

    variant = find_variant_by_id(variants, variant_id, input_file, working_file)

    hyperparameters = variant.get("hyperparameters", {})
    if not hyperparameters:
        logger.warning("Variant %s has no hyperparameters in metadata", variant_id)

    cv_score = None
    fold_scores = None
    feature_filename_from_metadata = variant.get("feature_filename")

    if feature_filename:
        input_metadata_dir = find_metadata_dir()
        cv_score, fold_scores = load_gridsearch_scores(
            regression_model_type, variant_id, feature_filename, input_metadata_dir
        )
        if cv_score is not None:
            feature_filename_from_metadata = feature_filename

    return {
        "variant": variant,
        "variant_id": variant_id,
        "cv_score": cv_score,
        "hyperparameters": hyperparameters,
        "feature_filename": feature_filename_from_metadata,
        "fold_scores": fold_scores,
    }


def _validate_variant_hyperparameters(
    regression_model_type: str,
    variant_id: str,
    hyperparameters: Dict[str, Any],
) -> None:
    if hyperparameters is None or not hyperparameters:
        logger.warning(
            "hyperparameters is empty or None. "
            "Variant validation will be skipped."
        )
        return

    try:
        variant_info = load_regression_variant_from_metadata(
            regression_model_type=regression_model_type,
            variant_id=variant_id,
        )
        variant_hyperparams = variant_info.get("hyperparameters", {})
        if variant_hyperparams and variant_hyperparams != hyperparameters:
            logger.warning(
                "Hyperparameters mismatch for variant %s. "
                "Metadata has: %s, "
                "Provided: %s. "
                "Proceeding with save, but this may indicate an issue.",
                variant_id,
                variant_hyperparams,
                hyperparameters,
            )
        logger.info("Variant ID validated: %s exists in metadata.json", variant_id)
    except (FileNotFoundError, ValueError) as e:
        logger.warning(
            "Could not validate variant_id %s in metadata.json: %s. "
            "Proceeding with save anyway.",
            variant_id,
            e,
        )


def _load_and_merge_gridsearch_results(
    regression_model_type: str,
    gridsearch_file: Path,
) -> List[Dict[str, Any]]:
    input_metadata_dir = find_metadata_dir()
    if input_metadata_dir and is_kaggle_input(input_metadata_dir):
        input_gridsearch_file = input_metadata_dir / regression_model_type / "gridsearch_metadata.json"
    else:
        input_gridsearch_file = None

    merge_fn = lambda inp, wrk: merge_list_by_key_add_only(
        inp, wrk, key_fn=lambda r: (r.get("variant_id"), r.get("feature_filename"))
    )
    results = merge_json_from_input_and_working(
        input_gridsearch_file,
        gridsearch_file,
        merge_fn,
        expected_type=list,
        file_type="Regression gridsearch metadata JSON",
    )
    if results and input_gridsearch_file and input_gridsearch_file.exists():
        logger.debug("Loaded %s results from input and working", len(results))
    return results


def _find_existing_result_index(
    results: List[Dict[str, Any]],
    variant_id: str,
    feature_filename: str,
) -> Optional[int]:
    for idx, r in enumerate(results):
        if r.get("variant_id") == variant_id and r.get("feature_filename") == feature_filename:
            return idx
    return None


def _generate_model_index_and_id(
    results: List[Dict[str, Any]],
    existing_idx: Optional[int],
    model_index: Optional[int],
    model_id: Optional[str],
) -> Tuple[int, str]:
    if model_index is None:
        if existing_idx is not None:
            model_index = results[existing_idx].get("model_index")
            if model_index is None:
                existing_indices = [
                    r.get("model_index", -1) for r in results if r.get("model_index") is not None
                ]
                model_index = max(existing_indices) + 1 if existing_indices else 0
        else:
            existing_indices = [
                r.get("model_index", -1) for r in results if r.get("model_index") is not None
            ]
            model_index = max(existing_indices) + 1 if existing_indices else 0

    if model_id is None:
        model_id = f"{model_index:03d}"

    return model_index, model_id


def _create_or_update_result(
    results: List[Dict[str, Any]],
    existing_idx: Optional[int],
    result_entry: Dict[str, Any],
    variant_id: str,
    feature_filename: str,
) -> None:
    if existing_idx is not None:
        existing_model_index = results[existing_idx].get("model_index")
        new_model_index = result_entry.get("model_index")
        if existing_model_index is not None and existing_model_index != new_model_index:
            logger.warning(
                "Updating result with different model_index: "
                "existing=%s, new=%s. "
                "Using new model_index.",
                existing_model_index,
                new_model_index,
            )
        logger.info(
            "Updating existing grid search result: model_id=%s, %s on %s",
            result_entry.get("model_id"),
            variant_id,
            feature_filename,
        )
        results[existing_idx] = result_entry
    else:
        results.append(result_entry)
        logger.info(
            "Added new grid search result: model_id=%s, %s on %s (cv_score: %.4f)",
            result_entry.get("model_id"),
            variant_id,
            feature_filename,
            result_entry.get("cv_score", 0),
        )


def save_regression_gridsearch_result(
    regression_model_type: str,
    variant_id: str,
    feature_filename: str,
    cv_score: float,
    fold_scores: List[float],
    hyperparameters: Dict[str, Any],
    model_index: Optional[int] = None,
    model_id: Optional[str] = None,
) -> None:
    """
    Save regression grid search result to gridsearch_metadata.json.

    Each entry represents a trained model (combination of variant + feature file) and has its own
    model_index and model_id for organization.
    """
    validate_regression_model_type(regression_model_type)
    _validate_variant_hyperparameters(regression_model_type, variant_id, hyperparameters)

    metadata_dir = get_writable_metadata_dir()
    gridsearch_file = metadata_dir / regression_model_type / "gridsearch_metadata.json"

    results = _load_and_merge_gridsearch_results(regression_model_type, gridsearch_file)

    gridsearch_file.parent.mkdir(parents=True, exist_ok=True)

    existing_idx = _find_existing_result_index(results, variant_id, feature_filename)

    model_index, model_id = _generate_model_index_and_id(
        results, existing_idx, model_index, model_id
    )

    result_entry = {
        "model_index": model_index,
        "model_id": model_id,
        "variant_id": variant_id,
        "feature_filename": feature_filename,
        "cv_score": cv_score,
        "fold_scores": fold_scores,
    }

    _create_or_update_result(results, existing_idx, result_entry, variant_id, feature_filename)

    save_json(results, gridsearch_file)
    logger.info("Saved grid search result to %s", gridsearch_file)


def load_specific_variant_from_metadata(
    regression_model_type: str,
    variant_id: str,
    feature_filename: Optional[str],
    metadata_dir: Optional[Path],
) -> Dict[str, Any]:
    """Load specific variant from metadata with gridsearch score fallback."""
    variant_info = load_regression_variant_from_metadata(
        regression_model_type=regression_model_type,
        variant_id=variant_id,
        feature_filename=feature_filename,
    )

    if feature_filename and variant_info.get("cv_score") is None:
        results = load_gridsearch_metadata(regression_model_type, metadata_dir)
        for result in results:
            if result.get("variant_id") == variant_id and result.get("feature_filename") == feature_filename:
                variant_info["cv_score"] = result.get("cv_score")
                variant_info["fold_scores"] = result.get("fold_scores")
                break

    if variant_info.get("cv_score") is None:
        logger.warning(
            "Variant %s has no cv_score in metadata. "
            "This may indicate the variant hasn't been trained yet.",
            variant_id,
        )

    logger.info("✅ Using SPECIFIED regression variant: %s", variant_id)
    cv_score = variant_info.get("cv_score")
    if cv_score is not None:
        logger.info("   (CV score: %.4f)", cv_score)

    return {
        "variant": variant_info.get("variant", {}),
        "variant_id": variant_id,
        "cv_score": variant_info.get("cv_score"),
        "hyperparameters": variant_info.get("hyperparameters", {}),
        "feature_filename": variant_info.get("feature_filename") or feature_filename,
    }


def load_variant_from_gridsearch_fallback(
    regression_model_type: str,
    variant_id: str,
    feature_filename: Optional[str],
    metadata_dir: Optional[Path],
) -> Dict[str, Any]:
    """Load variant from gridsearch metadata as fallback when metadata.json fails."""
    logger.warning(
        "Could not load variant from metadata, falling back to gridsearch_metadata.json..."
    )
    results = load_gridsearch_metadata(regression_model_type, metadata_dir)

    matching_results = [
        r
        for r in results
        if r.get("variant_id") == variant_id
        and (not feature_filename or r.get("feature_filename") == feature_filename)
    ]

    if not matching_results:
        raise ValueError(
            f"Regression variant {variant_id} not found in gridsearch_metadata.json.\n"
            f"  Feature filename: {feature_filename or 'any'}\n"
            f"  Available variant IDs: {[r.get('variant_id') for r in results[:10]]}..."
        )

    variant = matching_results[0]
    if variant.get("cv_score") is None:
        raise ValueError(f"Regression variant {variant_id} has no valid cv_score (may have failed)")

    logger.info("✅ Using SPECIFIED regression variant from gridsearch: %s", variant_id)
    cv_score = variant.get("cv_score")
    if cv_score is not None:
        logger.info("   (CV score: %.4f)", cv_score)

    return {
        "variant": variant,
        "variant_id": variant_id,
        "cv_score": variant.get("cv_score"),
        "hyperparameters": variant.get("hyperparameters", {}),
        "feature_filename": variant.get("feature_filename") or feature_filename,
    }


def find_best_variant_info(
    regression_model_type: str,
    feature_filename: str,
    metadata_dir: Optional[Path],
) -> Dict[str, Any]:
    """Find and return info for best regression variant (highest CV score)."""
    variant = find_best_regression_variant(
        regression_model_type=regression_model_type,
        feature_filename=feature_filename,
        metadata_dir=metadata_dir,
    )

    if variant is None:
        raise ValueError(
            f"No valid regression variants found for:\n"
            f"  Regression model type: {regression_model_type}\n"
            f"  Feature filename: {feature_filename}\n"
            f"  Please ensure regression grid search has been run."
        )

    variant_id = variant.get("variant_id")
    cv_score = variant.get("cv_score")
    hyperparameters = variant.get("hyperparameters", {})
    variant_feature_filename = variant.get("feature_filename")

    logger.info("✅ Using BEST regression variant: %s", variant_id)
    logger.info("   (Highest CV score: %.4f)", cv_score)
    logger.info("  Variant ID: %s", variant_id)
    logger.info("  CV Score: %.4f", cv_score)
    logger.info("  Hyperparameters: %s", hyperparameters)
    logger.info("  Feature Filename: %s", variant_feature_filename)

    return {
        "variant": variant,
        "variant_id": variant_id,
        "cv_score": cv_score,
        "hyperparameters": hyperparameters,
        "feature_filename": variant_feature_filename,
    }


def get_regression_variant_info(
    regression_model_type: str,
    feature_filename: Optional[str] = None,
    variant_id: Optional[str] = None,
    metadata_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Get information about a regression variant (or best variant) from regression grid search results.

    When variant_id is None, finds the variant with highest CV score (requires feature_filename).
    """
    if variant_id:
        try:
            return load_specific_variant_from_metadata(
                regression_model_type, variant_id, feature_filename, metadata_dir
            )
        except (FileNotFoundError, ValueError):
            return load_variant_from_gridsearch_fallback(
                regression_model_type, variant_id, feature_filename, metadata_dir
            )
    else:
        if not feature_filename:
            raise ValueError(
                "feature_filename is required when variant_id is None (best variant selection). "
                "Cannot determine best variant without knowing which feature file was used."
            )
        return find_best_variant_info(regression_model_type, feature_filename, metadata_dir)
