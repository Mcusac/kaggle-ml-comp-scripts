"""Seed working metadata files and load merged gridsearch result lists (CSIRO level_2)."""

import shutil

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger, is_kaggle_input
from layers.layer_0_core.level_4 import save_json
from layers.layer_0_core.level_5 import merge_json_from_input_and_working, merge_list_by_key_working_replaces

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    find_metadata_dir,
    get_writable_metadata_dir,
    validate_regression_model_type,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import is_empty_list_json

logger = get_logger(__name__)


def initialize_working_metadata_files(
    regression_model_type: str,
    force_refresh: bool = False,
) -> Tuple[Path, Path]:
    """
    Initialize working metadata directory by seeding from input if needed.

    By default this is non-destructive: it copies metadata files from the Kaggle input
    dataset into the writable working directory only if the working files don't exist.
    Set force_refresh=True to overwrite working files with the current input versions.

    Args:
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge')
        force_refresh: If True, overwrite working files with input copies

    Returns:
        Tuple of (metadata_file_path, gridsearch_file_path) in working directory.
    """
    validate_regression_model_type(regression_model_type)

    working_dir = get_writable_metadata_dir() / regression_model_type
    working_dir.mkdir(parents=True, exist_ok=True)

    input_dir = find_metadata_dir()
    input_metadata_file = None
    input_gridsearch_file = None

    if input_dir:
        input_metadata_file = input_dir / regression_model_type / "metadata.json"
        input_gridsearch_file = input_dir / regression_model_type / "gridsearch_metadata.json"

    working_metadata_file = working_dir / "metadata.json"
    working_gridsearch_file = working_dir / "gridsearch_metadata.json"

    if (
        input_metadata_file
        and input_metadata_file.exists()
        and input_metadata_file.resolve() != working_metadata_file.resolve()
        and (
            force_refresh
            or not working_metadata_file.exists()
            or is_empty_list_json(working_metadata_file)
        )
    ):
        shutil.copy2(input_metadata_file, working_metadata_file)
        logger.info("Seeded metadata.json from input to working: %s", working_metadata_file)
    elif not working_metadata_file.exists():
        working_metadata_file.parent.mkdir(parents=True, exist_ok=True)
        save_json([], working_metadata_file)
        logger.info("Created new metadata.json in working directory: %s", working_metadata_file)

    if (
        input_gridsearch_file
        and input_gridsearch_file.exists()
        and input_gridsearch_file.resolve() != working_gridsearch_file.resolve()
        and (
            force_refresh
            or not working_gridsearch_file.exists()
            or is_empty_list_json(working_gridsearch_file)
        )
    ):
        shutil.copy2(input_gridsearch_file, working_gridsearch_file)
        logger.info("Seeded gridsearch_metadata.json from input to working: %s", working_gridsearch_file)
    elif not working_gridsearch_file.exists():
        save_json([], working_gridsearch_file)
        logger.info(
            "Created new gridsearch_metadata.json in working directory: %s",
            working_gridsearch_file,
        )

    return working_metadata_file, working_gridsearch_file


def load_regression_gridsearch_results(
    regression_model_type: str,
    variant_id: Optional[str] = None,
    feature_filename: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Load regression grid search results from gridsearch_metadata.json.

    Loads from both input and working directories, merging results.
    Working directory entries take precedence for duplicates.
    Can filter by variant_id, feature_filename, or both.
    """
    validate_regression_model_type(regression_model_type)

    input_metadata_dir = find_metadata_dir()
    if input_metadata_dir is None:
        return []

    if is_kaggle_input(input_metadata_dir):
        input_gridsearch_file = input_metadata_dir / regression_model_type / "gridsearch_metadata.json"
        working_gridsearch_file = (
            get_writable_metadata_dir() / regression_model_type / "gridsearch_metadata.json"
        )
    else:
        input_gridsearch_file = None
        working_gridsearch_file = input_metadata_dir / regression_model_type / "gridsearch_metadata.json"

    merge_fn = lambda inp, wrk: merge_list_by_key_working_replaces(
        inp, wrk, key_fn=lambda r: (r.get("variant_id"), r.get("feature_filename"))
    )
    results = merge_json_from_input_and_working(
        input_gridsearch_file,
        working_gridsearch_file,
        merge_fn,
        expected_type=list,
        file_type="Regression gridsearch metadata JSON",
    )

    filtered_results = []
    for result in results:
        if variant_id and result.get("variant_id") != variant_id:
            continue
        if feature_filename and result.get("feature_filename") != feature_filename:
            continue
        filtered_results.append(result)

    return filtered_results
