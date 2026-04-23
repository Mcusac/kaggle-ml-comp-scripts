"""Orchestration for regression-based submissions (feature extraction + predict + save)."""

import numpy as np

from typing import Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_pickle
from layers.layer_0_core.level_5 import save_submission_csv

from layers.layer_1_competition.level_0_infra.level_2 import extract_test_features_from_model
from layers.layer_1_competition.level_0_infra.level_5 import (
    expand_predictions_to_submission_format,
)

_logger = get_logger(__name__)


def _load_regression_model_from_path(regression_model_path: str) -> Any:
    _logger.info("Loading regression model...")
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
        dataset_type="split",
        config=config,
        data_schema=data_schema,
        feature_extraction_model_name=feature_extraction_model_name,
    )

    _logger.info("Making predictions...")
    predictions = regression_model.predict(features)
    if isinstance(predictions, np.ndarray) and predictions.ndim == 1:
        predictions = predictions.reshape(-1, 1)

    _logger.info("Expanding predictions to submission format...")
    submission_df = expand_predictions_to_submission_format(
        predictions,
        test_csv_path,
        contest_config=config,
        data_schema=data_schema,
        post_processor=post_processor,
    )

    _logger.info(f"Saving submission to {output_path}...")
    save_submission_csv(submission_df, output_path)
    _logger.info("✅ Regression submission created successfully!")

