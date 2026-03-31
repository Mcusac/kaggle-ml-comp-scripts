"""Stacking pipeline for CSIRO contest."""

import pandas as pd

from pathlib import Path
from typing import Optional, Dict, Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import get_contest
from layers.layer_1_competition.level_0_infra.level_2 import (
    extract_test_features_from_model,
)
from layers.layer_1_competition.level_0_infra.submission import expand_predictions_to_submission_format, save_submission

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    create_and_train_stacking_ensemble,
    load_model_metadata,
    load_training_features,
)

logger = get_logger(__name__)


def stacking_pipeline(
    data_root: Optional[str] = None,
    stacking_config: Optional[Dict[str, Any]] = None,
    dataset_type: str = 'split',
    test_filename: str = 'test.csv',
    **kwargs
) -> pd.DataFrame:
    """
    Run stacking pipeline with Ridge meta-model.
    """
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()
    data_schema = contest['data_schema']()
    post_processor = contest['post_processor']()

    if data_root is None:
        data_root = str(paths.get_data_root())

    if stacking_config is None:
        stacking_config = {
            'model_paths': [],
            'meta_model_alpha': 10.0,
            'n_folds': 5
        }

    model_paths = stacking_config.get('model_paths', [])
    if not model_paths:
        raise ValueError("stacking_config must contain 'model_paths' list")

    meta_model_alpha = stacking_config.get('meta_model_alpha', 10.0)
    n_folds = stacking_config.get('n_folds', 5)

    logger.info("=" * 60)
    logger.info("Stacking Pipeline")
    logger.info("=" * 60)
    logger.info(f"  Base models: {len(model_paths)}")
    logger.info(f"  Meta-model alpha: {meta_model_alpha}")
    logger.info(f"  CV folds: {n_folds}")

    test_csv_path = Path(data_root) / test_filename
    if not test_csv_path.exists():
        raise FileNotFoundError(f"Test CSV not found: {test_csv_path}")

    logger.info("Loading model metadata...")
    model_configs, feature_extraction_model_name = load_model_metadata(model_paths)
    logger.info(f"Feature extraction model: {feature_extraction_model_name}")

    all_features, all_targets, fold_assignments, cache_metadata = load_training_features(
        model_configs, feature_extraction_model_name
    )

    test_features = extract_test_features_from_model(
        test_csv_path=test_csv_path,
        data_root=data_root,
        dataset_type=dataset_type,
        config=config,
        data_schema=data_schema,
        feature_extraction_model_name=feature_extraction_model_name,
    )

    final_predictions, oof_score = create_and_train_stacking_ensemble(
        model_paths, model_configs, feature_extraction_model_name,
        all_features, all_targets, test_features,
        n_folds, meta_model_alpha, config
    )

    logger.info("Expanding predictions to submission format...")
    submission_df = expand_predictions_to_submission_format(
        predictions=final_predictions,
        test_csv_path=str(test_csv_path),
        contest_config=config,
        data_schema=data_schema,
        post_processor=post_processor
    )

    output_path = str(paths.get_output_dir() / 'submission.csv')
    save_submission(submission_df, output_path=output_path)

    logger.info("=" * 60)
    logger.info("✅ Stacking Pipeline Complete")
    logger.info("=" * 60)
    logger.info(f"  Base models: {len(model_paths)}")
    logger.info(f"  OOF score: {oof_score:.4f}")
    logger.info(f"  Output: {output_path}")

    return submission_df
