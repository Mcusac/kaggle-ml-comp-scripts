"""Feature cache IO: save, load, locate, and resolve extraction info from disk."""

import json
import numpy as np

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import (
    get_cache_base_paths, 
    get_model_name_from_model_id, 
    get_metadata_dir, 
    parse_feature_filename
)

logger = get_logger(__name__)

# Tracks files saved in the current process session for priority lookup.
_session_saved_paths: Dict[str, Path] = {}


def get_feature_cache_paths(filename: str) -> Tuple[Path, Path]:
    """Return (input_path, working_path) for a given cache filename.

    Args:
        filename: Cache filename, e.g. 'variant_0100_features.npz'.

    Returns:
        Tuple of (input_path, working_path) as absolute Path objects.
    """
    input_base, working_base = get_cache_base_paths()
    return input_base / filename, working_base / filename


def find_feature_cache(filename: str) -> Optional[Path]:
    """Locate an existing feature cache file.

    Search priority:
        1. A path saved during the current session (working or input).
        2. The input directory.
        3. The working directory.

    Args:
        filename: Cache filename to locate.

    Returns:
        Path to the cache file, or None if not found in any location.
    """
    input_path, working_path = get_feature_cache_paths(filename)
    if filename in _session_saved_paths:
        saved_path = _session_saved_paths[filename]
        if saved_path.exists():
            logger.info(f"Found feature cache from this session: {saved_path}")
            return saved_path
        del _session_saved_paths[filename]
    if input_path.exists():
        logger.info(f"Found feature cache in input directory: {input_path}")
        return input_path
    if working_path.exists():
        logger.info(f"Found feature cache in working directory: {working_path}")
        return working_path
    logger.debug(f"No feature cache found for filename: {filename}")
    return None


def save_features(
    all_features: np.ndarray,
    all_targets: np.ndarray,
    fold_assignments: np.ndarray,
    filename: str,
    model_name: str,
    dataset_type: str = "split",
    image_size: Optional[Tuple[int, int]] = None,
    preprocessing_list: Optional[list] = None,
    use_input_dir: bool = True,
) -> Path:
    """Save extracted features to the cache.

    Attempts to write to the input directory first. Falls back to the working
    directory automatically on read-only filesystem errors.

    Args:
        all_features: Feature array of shape (N, feature_dim).
        all_targets: Target array of shape (N,) or (N, num_targets).
        fold_assignments: Fold assignment array of shape (N,).
        filename: Target cache filename.
        model_name: Name of the model that produced the features.
        dataset_type: Dataset split identifier (default: 'split').
        image_size: Optional (height, width) tuple stored in metadata.
        preprocessing_list: Optional list of preprocessing step identifiers.
        use_input_dir: If True, attempt input directory first (default: True).

    Returns:
        Path where the cache was written.

    Raises:
        ValueError: If required arguments are missing or invalid.
        OSError: On non-read-only write failures.
    """
    if not filename:
        raise ValueError("filename is required")
    if all_features is None or all_targets is None:
        raise ValueError("all_features and all_targets are required")
    if fold_assignments is None:
        raise ValueError("fold_assignments is required")

    input_path, working_path = get_feature_cache_paths(filename)
    metadata = _build_metadata(
        filename, model_name, dataset_type, image_size, preprocessing_list,
        all_features, all_targets, fold_assignments,
    )

    if use_input_dir:
        try:
            _write_npz(input_path, all_features, all_targets, fold_assignments, metadata)
            _session_saved_paths[filename] = input_path
            return input_path
        except (OSError, PermissionError) as e:
            is_readonly = (
                isinstance(e, OSError) and getattr(e, "errno", None) == 30
            ) or isinstance(e, PermissionError)
            if is_readonly:
                logger.warning(f"Cannot write to input directory (read-only): {input_path}")
                logger.info(f"Falling back to working directory: {working_path}")
            else:
                raise

    _write_npz(working_path, all_features, all_targets, fold_assignments, metadata)
    _session_saved_paths[filename] = working_path
    return working_path


def load_features(cache_path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """Load a feature cache file from disk.

    Args:
        cache_path: Absolute path to the .npz cache file.

    Returns:
        Tuple of (all_features, all_targets, fold_assignments, metadata).

    Raises:
        FileNotFoundError: If the cache file does not exist.
        ValueError: If the cache file is not an all-features cache.
    """
    if not cache_path.exists():
        raise FileNotFoundError(f"Feature cache file not found: {cache_path}")
    data = np.load(cache_path, allow_pickle=True)
    metadata_str = data["metadata"].item() if "metadata" in data else "{}"
    metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else {}
    cache_type = metadata.get("cache_type", "all_features")
    if cache_type != "all_features":
        raise ValueError(
            f"Cache file is not an all-features cache (cache_type: {cache_type!r}). "
            "Only all-features caches are supported."
        )
    logger.info(f"Loaded all-features cache: {cache_path}")
    return data["all_features"], data["all_targets"], data["fold_assignments"], metadata


def resolve_extraction_info(feature_filename: str) -> Dict[str, Any]:
    """Resolve full extraction metadata from a feature cache filename.

    Parses the filename to extract model_id and combo_id, resolves the model
    name via the registered model ID map, then attempts to load preprocessing
    and augmentation lists from the combo metadata JSON on disk.

    Args:
        feature_filename: Cache filename, e.g. 'variant_0100_features.npz'.

    Returns:
        Dict with keys: model_name, model_id, combo_id, preprocessing_list,
        augmentation_list.
    """
    model_id, combo_id = parse_feature_filename(feature_filename)
    model_name = get_model_name_from_model_id(model_id)
    preprocessing_list: list = []
    augmentation_list: list = []

    try:
        metadata_dir = get_metadata_dir()
        if metadata_dir and metadata_dir.exists():
            combo_metadata_path = metadata_dir / "data_manipulation" / "metadata.json"
            if combo_metadata_path.exists():
                with open(combo_metadata_path) as f:
                    combos_list = json.load(f)
                for combo in combos_list:
                    if combo.get("combo_id") == combo_id:
                        preprocessing_list = combo.get("preprocessing_list", [])
                        augmentation_list = combo.get("augmentation_list", [])
                        break
    except Exception as e:
        logger.debug(f"Could not load combo metadata: {e}. Using empty lists.")

    return {
        "model_name": model_name,
        "model_id": model_id,
        "combo_id": combo_id,
        "preprocessing_list": preprocessing_list,
        "augmentation_list": augmentation_list,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_metadata(
    filename: str,
    model_name: str,
    dataset_type: str,
    image_size: Optional[Tuple[int, int]],
    preprocessing_list: Optional[list],
    all_features: np.ndarray,
    all_targets: np.ndarray,
    fold_assignments: np.ndarray,
) -> Dict[str, Any]:
    return {
        "filename": filename,
        "model_name": model_name,
        "dataset_type": dataset_type,
        "image_size": str(image_size) if image_size else None,
        "preprocessing_list": preprocessing_list or [],
        "cache_type": "all_features",
        "all_features_shape": list(all_features.shape),
        "all_targets_shape": list(all_targets.shape),
        "fold_assignments_shape": list(fold_assignments.shape),
        "n_samples": int(all_features.shape[0]),
    }


def _write_npz(
    save_path: Path,
    all_features: np.ndarray,
    all_targets: np.ndarray,
    fold_assignments: np.ndarray,
    metadata: Dict[str, Any],
) -> None:
    save_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        save_path,
        all_features=all_features,
        all_targets=all_targets,
        fold_assignments=fold_assignments,
        metadata=json.dumps(metadata),
    )
    logger.info(f"Saved all-features cache: {save_path}")