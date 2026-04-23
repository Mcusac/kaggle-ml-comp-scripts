"""End-to-end ensemble OOF prediction generation."""

import os
import tempfile
import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import get_device, create_kfold_splits, get_fold_data
from layers.layer_0_core.level_4 import load_json

from layers.layer_1_competition.level_0_infra.level_1 import get_contest

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import process_single_fold_for_e2e_ensemble, aggregate_train_csv

_logger = get_logger(__name__)


def _setup_end_to_end_ensemble(
    ensemble_config: Dict[str, Any],
    train_csv_path: str,
    test_csv_path: str,
    all_targets: np.ndarray,
    n_folds: int,
    random_state: int
) -> Tuple[Any, Any, Any, pd.DataFrame, pd.DataFrame, int, int, int]:
    """Setup and initialize end-to-end ensemble OOF generation."""

    contest = get_contest('csiro')
    config = contest['config']()
    data_schema = contest['data_schema']()

    model_paths = ensemble_config.get('model_paths', [])
    if not model_paths:
        raise ValueError("ensemble_config must contain 'model_paths' list")

    train_df = aggregate_train_csv(train_csv_path)

    train_df_with_folds = create_kfold_splits(
        data=train_df,
        n_folds=n_folds,
        shuffle=True,
        random_state=random_state
    )

    n_train = len(train_df_with_folds)
    n_targets = all_targets.shape[1]

    test_df = pd.read_csv(test_csv_path)
    n_test = len(test_df)

    return config, data_schema, model_paths, train_df_with_folds, test_df, n_train, n_targets, n_test


def _get_ensemble_weights(model_paths: List[str], score_type: str) -> Optional[List[float]]:
    """Get ensemble weights from model metadata."""
    if score_type != 'cv':
        return None

    cv_scores = []
    for model_path in model_paths:
        metadata_file = Path(model_path) / 'model_metadata.json'
        if metadata_file.exists():
            metadata = load_json(metadata_file)
            cv_scores.append(metadata.get('cv_score', 1.0))
        else:
            cv_scores.append(1.0)

    return cv_scores if cv_scores else None


def _generate_end_to_end_ensemble_oof_predictions(
    ensemble_config: Dict[str, Any],
    train_csv_path: str,
    test_csv_path: str,
    data_root: str,
    all_targets: np.ndarray,
    n_folds: int = 5,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate OOF predictions from an end-to-end ensemble using cross-validation."""
    config, data_schema, model_paths, train_df_with_folds, test_df, n_train, n_targets, n_test = _setup_end_to_end_ensemble(
        ensemble_config, train_csv_path, test_csv_path, all_targets, n_folds, random_state
    )

    method = ensemble_config.get('method', 'weighted_average')
    score_type = ensemble_config.get('score_type', 'cv')

    oof_predictions = np.zeros((n_train, n_targets), dtype=np.float32)
    test_predictions_accumulator = np.zeros((n_test, n_targets), dtype=np.float32)

    device = get_device('auto')
    weights = _get_ensemble_weights(model_paths, score_type)

    _logger.info(f"Generating OOF predictions for end-to-end ensemble with {len(model_paths)} models...")

    for fold in range(n_folds):
        _logger.info(f"\n{'='*60}")
        _logger.info(f"Processing fold {fold + 1}/{n_folds}")
        _logger.info(f"{'='*60}")

        val_data = get_fold_data(train_df_with_folds, fold=fold, train=False)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            val_data.to_csv(tmp_file.name, index=False)
            val_csv_path = tmp_file.name

        try:
            ensemble_val_pred, ensemble_test_pred, val_indices = process_single_fold_for_e2e_ensemble(
                fold, n_folds, train_df_with_folds, model_paths, config, data_schema,
                val_csv_path, test_csv_path, data_root, device, method, weights
            )

            if ensemble_val_pred is not None and ensemble_test_pred is not None and len(val_indices) > 0:
                oof_predictions[val_indices] = ensemble_val_pred
                test_predictions_accumulator += ensemble_test_pred

                _logger.info(f"  Stored OOF predictions for {len(val_data)} validation samples")
                _logger.info(f"  OOF predictions shape: {ensemble_val_pred.shape}")
                _logger.info(f"  Test predictions shape: {ensemble_test_pred.shape}")

        finally:
            if os.path.exists(val_csv_path):
                os.unlink(val_csv_path)

    test_predictions = test_predictions_accumulator

    _logger.info(f"\nEnd-to-end ensemble OOF generation complete")
    _logger.info(f"  OOF predictions: {oof_predictions.shape}")
    _logger.info(f"  Test predictions: {test_predictions.shape}")

    return oof_predictions, test_predictions


def generate_end_to_end_ensemble_oof_predictions_batch(
    end_to_end_ensembles: List[Dict[str, Any]],
    train_csv_path: str,
    test_csv_path: str,
    data_root: str,
    all_targets: Optional[np.ndarray],
    n_folds: int
) -> tuple[list, list]:
    """Generate OOF predictions from end-to-end ensembles."""
    ensemble_oof_preds = []
    ensemble_test_preds = []

    _logger.info("Generating end-to-end ensemble-level OOF predictions...")
    for idx, ensemble_config in enumerate(end_to_end_ensembles):
        _logger.info(f"Processing end-to-end ensemble {idx + 1}/{len(end_to_end_ensembles)}...")
        oof_pred, test_pred = _generate_end_to_end_ensemble_oof_predictions(
            ensemble_config=ensemble_config,
            train_csv_path=train_csv_path,
            test_csv_path=test_csv_path,
            data_root=data_root,
            all_targets=all_targets,
            n_folds=n_folds,
            random_state=42
        )
        ensemble_oof_preds.append(oof_pred)
        ensemble_test_preds.append(test_pred)
        _logger.info(f"  End-to-end ensemble {idx + 1} OOF shape: {oof_pred.shape}, test shape: {test_pred.shape}")

    return ensemble_oof_preds, ensemble_test_preds
