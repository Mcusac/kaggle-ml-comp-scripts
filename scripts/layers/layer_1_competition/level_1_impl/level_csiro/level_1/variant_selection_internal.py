"""Path resolution, JSON merge helpers, and hyperparameter signatures for variant metadata."""

import json
import numpy as np

from pathlib import Path
from typing import Any, Dict, Optional

from layers.layer_0_core.level_4 import load_json
from layers.layer_0_core.level_5 import merge_json_from_input_and_working, merge_list_by_key_add_only

from layers.layer_0_core.level_0 import is_kaggle_input

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import find_metadata_dir, get_writable_metadata_dir


def is_empty_list_json(path: Path) -> bool:
    """Return True if the file exists and contains an empty JSON list ([])."""
    try:
        if not path.exists():
            return False
        data = load_json(path, expected_type=list, file_type="Metadata JSON")
        return isinstance(data, list) and len(data) == 0
    except Exception:
        return False


def resolve_metadata_file_locations(
    regression_model_type: str,
) -> tuple[Optional[Path], Optional[Path]]:
    """
    Resolve metadata file locations (input vs working).

    Returns:
        Tuple of (input_metadata_file, working_metadata_file)

    Raises:
        FileNotFoundError: If metadata directory not found
    """
    input_metadata_dir = find_metadata_dir()
    if input_metadata_dir is None:
        raise FileNotFoundError(
            "csiro-metadata directory not found. "
            "Expected: /kaggle/input/csiro-metadata (Kaggle) or ../csiro-metadata (local)"
        )

    if is_kaggle_input(input_metadata_dir):
        input_file = input_metadata_dir / regression_model_type / "metadata.json"
        working_file = get_writable_metadata_dir() / regression_model_type / "metadata.json"
    else:
        input_file = None
        working_file = input_metadata_dir / regression_model_type / "metadata.json"

    return input_file, working_file


def load_and_merge_variants(
    input_file: Optional[Path],
    working_file: Optional[Path],
) -> list:
    """
    Load variants from both input and working metadata files and merge.

    Uses add-only merge: working adds variants whose variant_id not in input.
    """
    merge_fn = lambda inp, wrk: merge_list_by_key_add_only(
        inp, wrk, key_fn=lambda x: x.get("variant_id")
    )
    variants = merge_json_from_input_and_working(
        input_file,
        working_file,
        merge_fn,
        expected_type=list,
        file_type="Regression metadata JSON",
    )
    if not variants:
        raise FileNotFoundError(
            f"Regression metadata file not found in either location.\n"
            f"  Checked: {input_file if input_file else 'N/A'}\n"
            f"  Checked: {working_file if working_file else 'N/A'}"
        )
    return variants


def find_variant_by_id(
    variants: list,
    variant_id: str,
    input_file: Optional[Path],
    working_file: Optional[Path],
) -> dict:
    """Find variant by variant_id in variants list."""
    for v in variants:
        if v.get("variant_id") == variant_id:
            return v

    available_ids = [v.get("variant_id") for v in variants]
    checked_files = []
    if input_file and input_file.exists():
        checked_files.append(str(input_file))
    if working_file and working_file.exists():
        checked_files.append(str(working_file))
    files_str = "\n  ".join(checked_files) if checked_files else "No metadata files found"

    raise ValueError(
        f"Regression variant {variant_id} not found in metadata files.\n"
        f"  Checked files:\n  {files_str}\n"
        f"  Available variant IDs: {available_ids}"
    )


def load_gridsearch_scores(
    regression_model_type: str,
    variant_id: str,
    feature_filename: str,
    input_metadata_dir: Path,
) -> tuple[Optional[float], Optional[list]]:
    """Load CV scores from gridsearch metadata."""
    if is_kaggle_input(input_metadata_dir):
        input_gridsearch_file = input_metadata_dir / regression_model_type / "gridsearch_metadata.json"
        working_gridsearch_file = (
            get_writable_metadata_dir() / regression_model_type / "gridsearch_metadata.json"
        )
    else:
        input_gridsearch_file = None
        working_gridsearch_file = input_metadata_dir / regression_model_type / "gridsearch_metadata.json"

    merge_fn = lambda inp, wrk: merge_list_by_key_add_only(
        inp, wrk, key_fn=lambda r: (r.get("variant_id"), r.get("feature_filename"))
    )
    gridsearch_results = merge_json_from_input_and_working(
        input_gridsearch_file,
        working_gridsearch_file,
        merge_fn,
        expected_type=list,
        file_type="Regression gridsearch metadata JSON",
    )

    for result in gridsearch_results:
        if result.get("variant_id") == variant_id and result.get("feature_filename") == feature_filename:
            return result.get("cv_score"), result.get("fold_scores")

    return None, None


def to_jsonable(value: Any) -> Any:
    """Convert values to JSON-serializable primitives deterministically."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]

    try:
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except Exception:
        pass

    return str(value)


def hyperparameters_signature(hyperparameters: Dict[str, Any]) -> str:
    """Create a deterministic signature for a hyperparameters dict."""
    jsonable = to_jsonable(hyperparameters)
    return json.dumps(jsonable, sort_keys=True, separators=(",", ":"), default=str)
