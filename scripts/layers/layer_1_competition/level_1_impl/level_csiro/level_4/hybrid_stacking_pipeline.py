"""Hybrid stacking pipeline for CSIRO contest."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Optional, Dict, Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_5 import save_submission_csv

from layers.layer_1_competition.level_0_infra.level_1 import get_contest
from layers.layer_1_competition.level_0_infra.level_5 import (
    expand_predictions_to_submission_format,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    generate_end_to_end_ensemble_oof_predictions_batch,
    generate_final_predictions,
    train_meta_models,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_3 import (
    generate_regression_ensemble_oof_predictions,
    load_features_for_regression,
)

_logger = get_logger(__name__)


def hybrid_stacking_pipeline(
    data_root: Optional[str] = None,
    hybrid_stacking_config: Optional[Dict[str, Any]] = None,
    dataset_type: str = 'split',
    test_filename: str = 'test.csv',
    **kwargs
) -> pd.DataFrame:
    """
    Run hybrid stacking pipeline (regression + end-to-end ensembles).
    """
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()
    data_schema = contest['data_schema']()
    post_processor = contest['post_processor']()

    if data_root is None:
        data_root = str(paths.get_data_root())

    if hybrid_stacking_config is None:
        hybrid_stacking_config = {
            'regression_ensembles': [],
            'end_to_end_ensembles': [],
            'meta_model_alpha': 10.0,
            'n_folds': 5
        }

    regression_ensembles = hybrid_stacking_config.get('regression_ensembles', [])
    end_to_end_ensembles = hybrid_stacking_config.get('end_to_end_ensembles', [])

    meta_model_alpha = hybrid_stacking_config.get('meta_model_alpha', 10.0)
    n_folds = hybrid_stacking_config.get('n_folds', 5)

    _logger.info("=" * 60)
    _logger.info("Hybrid Stacking Pipeline")
    _logger.info("=" * 60)
    _logger.info(f"  Regression ensembles: {len(regression_ensembles)}")
    _logger.info(f"  End-to-end ensembles: {len(end_to_end_ensembles)}")
    _logger.info(f"  Meta-model alpha: {meta_model_alpha}")
    _logger.info(f"  CV folds: {n_folds}")

    if not regression_ensembles and not end_to_end_ensembles:
        raise ValueError("At least one regression or end-to-end ensemble must be provided")

    test_csv_path = Path(data_root) / test_filename
    if not test_csv_path.exists():
        raise FileNotFoundError(f"Test CSV not found: {test_csv_path}")

    all_features = None
    all_targets = None
    test_features = None

    if regression_ensembles:
        all_features, all_targets, test_features = load_features_for_regression(
            regression_ensembles, data_root, dataset_type, test_csv_path, config, data_schema
        )

    ensemble_oof_preds = []
    ensemble_test_preds = []

    if regression_ensembles:
        reg_oof, reg_test = generate_regression_ensemble_oof_predictions(
            regression_ensembles, all_features, all_targets, test_features, n_folds
        )
        ensemble_oof_preds.extend(reg_oof)
        ensemble_test_preds.extend(reg_test)

    if end_to_end_ensembles:
        train_csv_path = str(Path(data_root) / 'train.csv')
        e2e_oof, e2e_test = generate_end_to_end_ensemble_oof_predictions_batch(
            end_to_end_ensembles, train_csv_path, str(test_csv_path),
            data_root, all_targets, n_folds
        )
        ensemble_oof_preds.extend(e2e_oof)
        ensemble_test_preds.extend(e2e_test)

    n_targets = all_targets.shape[1] if all_targets is not None else len(config.primary_targets)
    meta_models, oof_score = train_meta_models(
        ensemble_oof_preds, all_targets, config, meta_model_alpha
    )

    final_predictions = generate_final_predictions(
        ensemble_test_preds, meta_models, n_targets
    )

    _logger.info("Expanding predictions to submission format...")
    submission_df = expand_predictions_to_submission_format(
        predictions=final_predictions,
        test_csv_path=str(test_csv_path),
        contest_config=config,
        data_schema=data_schema,
        post_processor=post_processor
    )

    output_path = str(paths.get_output_dir() / 'submission.csv')
    save_submission_csv(submission_df, output_path=output_path)

    _logger.info("=" * 60)
    _logger.info("Hybrid Stacking Pipeline Complete")
    _logger.info("=" * 60)
    _logger.info(f"  Regression ensembles: {len(regression_ensembles)}")
    _logger.info(f"  End-to-end ensembles: {len(end_to_end_ensembles)}")
    if all_targets is not None and meta_models:
        _logger.info(f"  OOF score: {oof_score:.4f}")
    _logger.info(f"  Output: {output_path}")

    return submission_df
