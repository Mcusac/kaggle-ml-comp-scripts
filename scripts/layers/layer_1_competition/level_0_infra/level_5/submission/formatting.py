"""Submission formatting: build submission rows from predictions."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, Dict, List

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_5 import load_and_validate_test_data

_logger = get_logger(__name__)


def expand_predictions_to_submission_format(
    predictions: np.ndarray,
    test_csv_path: str,
    *,
    contest_config: Any,
    data_schema: Any,
    post_processor: Any,
) -> pd.DataFrame:
    """
    Expand primary predictions to all targets, apply post-processing, build submission rows.
    Uses only contest config, data_schema, post_processor (no evaluation_constants).
    """
    if not isinstance(predictions, np.ndarray) or predictions.ndim != 2:
        raise ValueError(
            f"predictions must be 2D numpy array, got {type(predictions)} shape {getattr(predictions, 'shape', None)}"
        )
    n_prim = contest_config.num_primary_targets
    if predictions.shape[1] != n_prim:
        raise ValueError(f"predictions must have {n_prim} columns, got {predictions.shape[1]}")
    if not test_csv_path or not isinstance(test_csv_path, str):
        raise ValueError("test_csv_path must be non-empty string")

    unique = load_and_validate_test_data(test_csv_path, image_path_column=data_schema.image_path_column)
    if len(unique) != predictions.shape[0]:
        raise ValueError(f"Unique images ({len(unique)}) != predictions rows ({predictions.shape[0]})")

    all_targets_arr = contest_config.compute_derived_targets(predictions)
    all_targets_arr = post_processor.apply(all_targets_arr)

    unique = unique.reset_index(drop=True)
    rows: List[Dict[str, Any]] = []
    for pos in range(len(unique)):
        row = unique.iloc[pos]
        image_id = Path(row[data_schema.image_path_column]).stem
        for i, target_name in enumerate(contest_config.all_targets):
            val = float(all_targets_arr[pos, i])
            sample_id = data_schema.format_sample_id(image_id, target_name)
            rows.append({"sample_id": sample_id, "target": val})

    df = pd.DataFrame(rows)
    expected = len(unique) * len(contest_config.all_targets)
    if len(df) != expected:
        raise ValueError(f"Submission rows {len(df)} != expected {expected}")
    _logger.info(f"Expanded {len(unique)} images to {len(df)} submission rows")
    return df

