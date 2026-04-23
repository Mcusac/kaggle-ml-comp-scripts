"""Meta-model training and prediction for hybrid stacking."""

import numpy as np

from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import get_ridge

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import calc_metric

_logger = get_logger(__name__)


def _build_meta_features(
    ensemble_oof_preds: list,
    target_idx: int
) -> np.ndarray:
    """Build meta-features by stacking ensemble predictions for a target."""
    return np.column_stack([
        ensemble_oof[:, target_idx]
        for ensemble_oof in ensemble_oof_preds
    ])


def _train_single_meta_model(
    target_idx: int,
    X_meta: np.ndarray,
    y_meta: np.ndarray,
    meta_model_alpha: float
) -> Any:
    """Train a single Ridge meta-model for a target."""
    Ridge = get_ridge()
    meta_model = Ridge(alpha=meta_model_alpha, random_state=42)
    meta_model.fit(X_meta, y_meta)

    coef_str = ', '.join([
        f"Ensemble_{i+1}: {coef:.3f}"
        for i, coef in enumerate(meta_model.coef_)
    ])
    _logger.info(f"  Target {target_idx} weights -> {coef_str}")

    return meta_model


def _calculate_meta_model_oof_score(
    ensemble_oof_preds: list,
    all_targets: np.ndarray,
    meta_models: dict,
    config: Any
) -> float:
    """Calculate OOF score using meta-models."""
    oof_combined = np.zeros_like(all_targets)
    for target_idx, meta_model in meta_models.items():
        X_meta = _build_meta_features(ensemble_oof_preds, target_idx)
        oof_combined[:, target_idx] = meta_model.predict(X_meta)

    oof_combined = np.clip(oof_combined, 0, None)
    oof_score, _ = calc_metric(oof_combined, all_targets, config=config)
    _logger.info(f"Hybrid Stacking OOF Score: {oof_score:.4f}")
    return oof_score


def train_meta_models(
    ensemble_oof_preds: list,
    all_targets: Optional[np.ndarray],
    config: Any,
    meta_model_alpha: float
) -> tuple[dict, Optional[float]]:
    """Train meta-models (Ridge) per target on combined ensemble OOF predictions."""
    _logger.info("Training meta-models on combined ensemble predictions...")

    n_targets = all_targets.shape[1] if all_targets is not None else len(config.primary_targets)
    meta_models = {}

    for target_idx in range(n_targets):
        X_meta = _build_meta_features(ensemble_oof_preds, target_idx)

        if all_targets is not None:
            y_meta = all_targets[:, target_idx]
            meta_model = _train_single_meta_model(target_idx, X_meta, y_meta, meta_model_alpha)
            meta_models[target_idx] = meta_model
        else:
            _logger.warning(f"No training targets available for target {target_idx}, skipping meta-model training")

    _logger.info(f"Trained {len(meta_models)} meta-models")

    oof_score = None
    if all_targets is not None and meta_models:
        oof_score = _calculate_meta_model_oof_score(ensemble_oof_preds, all_targets, meta_models, config)
    else:
        _logger.warning("Cannot calculate OOF score: targets or meta-models not available")

    return meta_models, oof_score


def generate_final_predictions(
    ensemble_test_preds: list,
    meta_models: dict,
    n_targets: int
) -> np.ndarray:
    """Generate final test predictions using meta-models."""
    _logger.info("Generating final test predictions...")
    n_test = ensemble_test_preds[0].shape[0] if ensemble_test_preds else 0
    final_predictions = np.zeros((n_test, n_targets))

    for target_idx, meta_model in meta_models.items():
        X_meta = np.column_stack([
            ensemble_test[:, target_idx]
            for ensemble_test in ensemble_test_preds
        ])
        final_predictions[:, target_idx] = meta_model.predict(X_meta)

    final_predictions = np.clip(final_predictions, 0, None)
    _logger.info(f"Final predictions shape: {final_predictions.shape}")
    return final_predictions
