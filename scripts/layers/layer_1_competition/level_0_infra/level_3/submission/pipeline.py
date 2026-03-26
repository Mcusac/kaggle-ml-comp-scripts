"""expand_predictions_to_submission_format, save_submission; contest config, data_schema, post_processor only."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, Dict, List, Optional

from layers.layer_0_core.level_0 import get_logger, is_kaggle
from layers.layer_0_core.level_1 import resolve_environment_path
from layers.layer_0_core.level_4 import load_pickle
from layers.layer_0_core.level_5 import load_and_validate_test_data

from layers.layer_1_competition.level_0_infra.level_2 import extract_test_features_from_model

logger = get_logger(__name__)


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
        raise ValueError(f"predictions must be 2D numpy array, got {type(predictions)} shape {getattr(predictions, 'shape', None)}")
    n_prim = contest_config.num_primary_targets
    if predictions.shape[1] != n_prim:
        raise ValueError(f"predictions must have {n_prim} columns, got {predictions.shape[1]}")
    if not test_csv_path or not isinstance(test_csv_path, str):
        raise ValueError("test_csv_path must be non-empty string")

    unique = load_and_validate_test_data(test_csv_path, image_path_column=data_schema.image_path_column)
    if len(unique) != predictions.shape[0]:
        raise ValueError(
            f"Unique images ({len(unique)}) != predictions rows ({predictions.shape[0]})"
        )

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
            rows.append({'sample_id': sample_id, 'target': val})

    df = pd.DataFrame(rows)
    expected = len(unique) * len(contest_config.all_targets)
    if len(df) != expected:
        raise ValueError(f"Submission rows {len(df)} != expected {expected}")
    logger.info(f"Expanded {len(unique)} images to {len(df)} submission rows")
    return df


def save_submission(submission_df: pd.DataFrame, output_path: Optional[str] = None) -> str:
    """
    Save submission CSV. Default: environment output root / submission.csv.
    On Kaggle, if path is not /kaggle/working/submission.csv, also writes there.
    """
    out = output_path or str(resolve_environment_path('submission.csv', purpose='output'))
    submission_df.to_csv(out, index=False)
    if is_kaggle():
        kw = '/kaggle/working/submission.csv'
        if str(Path(out).resolve()) != kw:
            submission_df.to_csv(kw, index=False)
            logger.info(f"Also wrote {kw}")
    return str(out)


def _load_regression_model_from_path(regression_model_path: str) -> Any:
    """Load regression model from pickle file."""
    logger.info("Loading regression model...")
    return load_pickle(regression_model_path)


def create_regression_submission(
    regression_model_path: str,
    feature_extraction_model_name: str,
    test_csv_path: str,
    data_root: str,
    config: Any,
    device: Any,
    output_path: str,
    data_schema: Any,
    post_processor: Any,
) -> None:
    """
    Create submission using regression model with feature extraction.
    data_schema and post_processor must be provided by caller (contest context).
    """
    regression_model = _load_regression_model_from_path(regression_model_path)

    features = extract_test_features_from_model(
        test_csv_path=test_csv_path,
        data_root=data_root,
        dataset_type='split',
        config=config,
        data_schema=data_schema,
        feature_extraction_model_name=feature_extraction_model_name,
    )

    logger.info("Making predictions...")
    predictions = regression_model.predict(features)
    if predictions.ndim == 1:
        predictions = predictions.reshape(-1, 1)

    logger.info("Expanding predictions to submission format...")
    submission_df = expand_predictions_to_submission_format(
        predictions,
        test_csv_path,
        contest_config=config,
        data_schema=data_schema,
        post_processor=post_processor,
    )

    logger.info(f"Saving submission to {output_path}...")
    save_submission(submission_df, output_path)
    logger.info("✅ Regression submission created successfully!")
