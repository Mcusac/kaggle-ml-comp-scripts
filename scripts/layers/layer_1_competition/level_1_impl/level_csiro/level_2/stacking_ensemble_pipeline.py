"""Stacking ensemble pipeline for CSIRO contest."""

import numpy as np
import pandas as pd
import sys

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# For lazy sklearn loading patterns, see ``layers.layer_0_core.level_2.models.sklearn_imports``.
from sklearn.model_selection import KFold
from sklearn.linear_model import Ridge

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import find_feature_cache, load_features
from layers.layer_0_core.level_3 import create_regression_model
from layers.layer_0_core.level_4 import load_pickle
from layers.layer_0_core.level_7 import create_ensembling_method

from layers.layer_1_competition.level_0_infra.level_1 import get_contest
from layers.layer_1_competition.level_0_infra.level_2 import (
    extract_test_features_from_model,
)
from layers.layer_1_competition.level_0_infra.level_3.submission import (
    expand_predictions_to_submission_format,
    save_submission,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import calc_metric
from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    csiro_modeling,
    resolve_model_paths_from_config,
)

logger = get_logger(__name__)


def _resolve_ensemble_model_paths(ensemble_config: Dict[str, Any]) -> Tuple[List[str], Optional[List[float]]]:
    """Resolve model paths and get CV scores from ensemble config."""
    model_paths = ensemble_config.get('model_paths', [])
    if not model_paths:
        raise ValueError("ensemble_config must contain 'model_paths' list")

    base_model_dir = ensemble_config.get('base_model_dir')
    if base_model_dir:
        resolved_paths, cv_scores, _ = resolve_model_paths_from_config(
            ensemble_config,
            base_model_dir=base_model_dir,
            auto_detect=False
        )
        return resolved_paths, cv_scores

    return model_paths, None


def _load_regression_model(model_path: str) -> Any:
    """Load a regression model from pickle file."""

    model_path_obj = Path(model_path)
    model_file = model_path_obj / 'regression_model.pkl'

    if not model_file.exists():
        if model_path_obj.suffix == '.pkl' and model_path_obj.exists():
            model_file = model_path_obj
        else:
            raise FileNotFoundError(f"Regression model not found: {model_path}")

    if 'modeling' not in sys.modules:
        try:
            sys.modules['modeling'] = csiro_modeling
        except Exception:
            pass
    return load_pickle(model_file)


def _train_and_predict_fold(
    model_path: str,
    X_tr: np.ndarray,
    y_tr: np.ndarray,
    X_val: np.ndarray,
    test_features: np.ndarray,
    random_state: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Train a model on fold data and predict on validation and test."""
    model = _load_regression_model(model_path)

    model_type = getattr(model, 'model_type', None)
    model_params = getattr(model, 'model_params', {})

    model_fold = create_regression_model(
        model_type or 'lgbm',
        **model_params
    )

    model_fold.fit(X_tr, y_tr)

    val_pred = model_fold.predict(X_val)
    if val_pred.ndim == 1:
        val_pred = val_pred.reshape(-1, 1)
    val_pred = np.clip(val_pred, 0, None)

    test_pred = model_fold.predict(test_features)
    if test_pred.ndim == 1:
        test_pred = test_pred.reshape(-1, 1)
    test_pred = np.clip(test_pred, 0, None)

    return val_pred, test_pred


def _combine_fold_predictions(
    fold_oof_preds: List[np.ndarray],
    fold_test_preds: List[np.ndarray],
    method: str,
    weights: Optional[List[float]],
    n_folds: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Combine individual model predictions using ensemble method."""

    ensembling_method = create_ensembling_method(method)

    ensemble_oof = ensembling_method.combine(fold_oof_preds, weights)
    ensemble_oof = np.clip(ensemble_oof, 0, None)

    ensemble_test = ensembling_method.combine(fold_test_preds, weights)
    ensemble_test = np.clip(ensemble_test, 0, None)

    return ensemble_oof, ensemble_test / n_folds


def generate_ensemble_oof_predictions(
    ensemble_config: Dict[str, Any],
    all_features: np.ndarray,
    all_targets: np.ndarray,
    test_features: np.ndarray,
    n_folds: int = 5,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate OOF predictions from an ensemble using cross-validation."""
    model_paths, cv_scores = _resolve_ensemble_model_paths(ensemble_config)
    method = ensemble_config.get('method', 'weighted_average')
    score_type = ensemble_config.get('score_type', 'cv')
    weights = cv_scores if (score_type == 'cv' and cv_scores) else None

    n_train = all_features.shape[0]
    n_test = test_features.shape[0]
    n_targets = all_targets.shape[1]

    oof_predictions = np.zeros((n_train, n_targets))
    test_predictions = np.zeros((n_test, n_targets))

    kf = KFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    for fold, (train_idx, val_idx) in enumerate(kf.split(all_features, all_targets)):
        logger.info(f"  Ensemble fold {fold + 1}/{n_folds}")

        X_tr, X_val = all_features[train_idx], all_features[val_idx]
        y_tr = all_targets[train_idx]

        fold_oof_preds = []
        fold_test_preds = []

        for model_path in model_paths:
            val_pred, test_pred = _train_and_predict_fold(
                model_path, X_tr, y_tr, X_val, test_features, random_state
            )
            fold_oof_preds.append(val_pred)
            fold_test_preds.append(test_pred)

        ensemble_oof, ensemble_test = _combine_fold_predictions(
            fold_oof_preds, fold_test_preds, method, weights, n_folds
        )

        oof_predictions[val_idx] = ensemble_oof
        test_predictions += ensemble_test

    return oof_predictions, test_predictions


def _find_feature_filename_from_ensembles(
    ensemble_configs: List[Dict[str, Any]],
) -> str:
    """Find feature filename from ensemble model metadata."""
    from layers.layer_1_competition.level_0_infra.level_2.feature_extraction import (
        find_feature_filename_from_ensemble_metadata,
    )

    return find_feature_filename_from_ensemble_metadata(
        ensemble_configs, metadata_key="model_paths"
    )


def _load_training_features(
    ensemble_configs: List[Dict[str, Any]]
) -> Tuple[np.ndarray, np.ndarray]:
    """Load training features and targets from cache."""
    feature_filename = _find_feature_filename_from_ensembles(ensemble_configs)

    cache_path = find_feature_cache(feature_filename)
    if not cache_path:
        raise FileNotFoundError(f"Feature file not found: {feature_filename}")

    logger.info(f"Loading features from {cache_path}")
    all_features, all_targets_from_cache, fold_assignments, cache_metadata = load_features(cache_path)
    all_targets = all_targets_from_cache

    logger.info(f"Loaded features: {all_features.shape}, targets: {all_targets.shape}")
    return all_features, all_targets


def _generate_ensemble_level_predictions(
    ensemble_configs: List[Dict[str, Any]],
    all_features: np.ndarray,
    all_targets: np.ndarray,
    test_features: np.ndarray,
    n_folds: int
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Generate OOF and test predictions from each ensemble."""
    ensemble_oof_preds = []
    ensemble_test_preds = []

    logger.info("Generating ensemble-level OOF predictions...")
    for idx, ensemble_config in enumerate(ensemble_configs):
        logger.info(f"Processing ensemble {idx + 1}/{len(ensemble_configs)}...")
        oof_pred, test_pred = generate_ensemble_oof_predictions(
            ensemble_config=ensemble_config,
            all_features=all_features,
            all_targets=all_targets,
            test_features=test_features,
            n_folds=n_folds,
            random_state=42
        )
        ensemble_oof_preds.append(oof_pred)
        ensemble_test_preds.append(test_pred)
        logger.info(f"  Ensemble {idx + 1} OOF shape: {oof_pred.shape}, test shape: {test_pred.shape}")

    return ensemble_oof_preds, ensemble_test_preds


def _train_stacking_meta_models(
    ensemble_oof_preds: List[np.ndarray],
    all_targets: np.ndarray,
    meta_model_alpha: float
) -> dict:
    """Train Ridge meta-models per target on ensemble OOF predictions."""

    logger.info("Training meta-models on ensemble predictions...")
    n_targets = all_targets.shape[1]
    meta_models = {}

    for target_idx in range(n_targets):
        X_meta = np.column_stack([
            ensemble_oof[:, target_idx]
            for ensemble_oof in ensemble_oof_preds
        ])

        y_meta = all_targets[:, target_idx]

        meta_model = Ridge(alpha=meta_model_alpha, random_state=42)
        meta_model.fit(X_meta, y_meta)
        meta_models[target_idx] = meta_model

        coef_str = ', '.join([
            f"Ensemble_{i+1}: {coef:.3f}"
            for i, coef in enumerate(meta_model.coef_)
        ])
        logger.info(f"  Target {target_idx} weights -> {coef_str}")

    logger.info(f"Trained {len(meta_models)} meta-models")
    return meta_models


def _calculate_stacking_oof_score(
    ensemble_oof_preds: List[np.ndarray],
    all_targets: np.ndarray,
    meta_models: dict,
    config: Any
) -> float:
    """Calculate OOF score for stacking ensemble."""
    oof_combined = np.zeros_like(all_targets)
    for target_idx, meta_model in meta_models.items():
        X_meta = np.column_stack([
            ensemble_oof[:, target_idx]
            for ensemble_oof in ensemble_oof_preds
        ])
        oof_combined[:, target_idx] = meta_model.predict(X_meta)

    oof_combined = np.clip(oof_combined, 0, None)
    oof_score, _ = calc_metric(oof_combined, all_targets, config=config)
    logger.info(f"Stacking Ensemble OOF Score: {oof_score:.4f}")
    return oof_score


def _generate_stacking_final_predictions(
    ensemble_test_preds: List[np.ndarray],
    meta_models: dict,
    n_test: int,
    n_targets: int
) -> np.ndarray:
    """Generate final test predictions using meta-models."""
    logger.info("Generating final test predictions...")
    final_predictions = np.zeros((n_test, n_targets))

    for target_idx, meta_model in meta_models.items():
        X_meta = np.column_stack([
            ensemble_test[:, target_idx]
            for ensemble_test in ensemble_test_preds
        ])
        final_predictions[:, target_idx] = meta_model.predict(X_meta)

    final_predictions = np.clip(final_predictions, 0, None)
    logger.info(f"Final predictions shape: {final_predictions.shape}")
    return final_predictions


def stacking_ensemble_pipeline(
    data_root: Optional[str] = None,
    stacking_ensemble_config: Optional[Dict[str, Any]] = None,
    dataset_type: str = 'split',
    test_filename: str = 'test.csv',
    **kwargs
) -> pd.DataFrame:
    """
    Run stacking pipeline with ensemble base models.
    """
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()
    data_schema = contest['data_schema']()
    post_processor = contest['post_processor']()

    if data_root is None:
        data_root = str(paths.get_data_root())

    if stacking_ensemble_config is None:
        stacking_ensemble_config = {
            'ensemble_configs': [],
            'meta_model_alpha': 10.0,
            'n_folds': 5
        }

    ensemble_configs = stacking_ensemble_config.get('ensemble_configs', [])
    if not ensemble_configs:
        raise ValueError("stacking_ensemble_config must contain 'ensemble_configs' list")

    meta_model_alpha = stacking_ensemble_config.get('meta_model_alpha', 10.0)
    n_folds = stacking_ensemble_config.get('n_folds', 5)

    logger.info("=" * 60)
    logger.info("Stacking Ensemble Pipeline")
    logger.info("=" * 60)
    logger.info(f"  Base ensembles: {len(ensemble_configs)}")
    logger.info(f"  Meta-model alpha: {meta_model_alpha}")
    logger.info(f"  CV folds: {n_folds}")

    test_csv_path = Path(data_root) / test_filename
    if not test_csv_path.exists():
        raise FileNotFoundError(f"Test CSV not found: {test_csv_path}")

    logger.info("Loading training features and targets...")
    all_features, all_targets = _load_training_features(ensemble_configs)

    test_features = extract_test_features_from_model(
        test_csv_path=test_csv_path,
        data_root=data_root,
        dataset_type=dataset_type,
        config=config,
        data_schema=data_schema,
        feature_extraction_model_name="dinov2_base",
    )

    ensemble_oof_preds, ensemble_test_preds = _generate_ensemble_level_predictions(
        ensemble_configs, all_features, all_targets, test_features, n_folds
    )

    meta_models = _train_stacking_meta_models(
        ensemble_oof_preds, all_targets, meta_model_alpha
    )

    oof_score = _calculate_stacking_oof_score(
        ensemble_oof_preds, all_targets, meta_models, config
    )

    final_predictions = _generate_stacking_final_predictions(
        ensemble_test_preds, meta_models, test_features.shape[0], all_targets.shape[1]
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
    logger.info("✅ Stacking Ensemble Pipeline Complete")
    logger.info("=" * 60)
    logger.info(f"  Base ensembles: {len(ensemble_configs)}")
    logger.info(f"  OOF score: {oof_score:.4f}")
    logger.info(f"  Output: {output_path}")

    return submission_df
