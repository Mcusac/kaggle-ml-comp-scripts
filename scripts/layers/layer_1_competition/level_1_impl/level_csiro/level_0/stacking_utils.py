"""Shared utilities for hybrid stacking pipeline. Breaks circular import between pipeline and helpers."""

import torch
import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import cleanup_gpu_memory, get_fold_data
from layers.layer_0_core.level_4 import load_json
from layers.layer_0_core.level_6 import create_test_dataloader
from layers.layer_0_core.level_7 import create_ensembling_method

from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model

logger = get_logger(__name__)


def _run_inference(model: Any, dataloader: Any, device: Any) -> np.ndarray:
    """Run inference on a dataloader."""
    predictions = []
    with torch.no_grad():
        for batch in dataloader:
            if isinstance(batch, (list, tuple)):
                images = batch[0]
            else:
                images = batch
            images = images.to(device)
            outputs = model(images)
            predictions.append(outputs.detach().cpu().numpy())
    return np.concatenate(predictions, axis=0)


def load_and_run_model_inference(
    model_path: Path,
    config: Any,
    data_schema: Any,
    val_csv_path: str,
    test_csv_path: str,
    data_root: str,
    device: Any
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Load a single model and run inference on validation and test sets."""
    checkpoint_path = model_path / 'best_model.pth'
    if not checkpoint_path.exists():
        logger.warning(f"Checkpoint not found: {checkpoint_path}, skipping")
        return None, None

    # Load model metadata
    metadata_file = model_path / 'model_metadata.json'
    if metadata_file.exists():
        metadata = load_json(metadata_file)
        model_name = metadata.get('model_name', 'dinov2_base')
        dataset_type = metadata.get('dataset_type', 'split')
    else:
        model_name = 'dinov2_base'
        dataset_type = 'split'

    # Create and load model
    model = create_feature_extraction_model(
        model_name=model_name,
        num_primary_targets=len(config.primary_targets),
        device=device,
        image_size=None,
        pretrained=False
    )

    checkpoint = torch.load(checkpoint_path, map_location=device)
    if isinstance(model, torch.nn.DataParallel):
        model.module.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint['model_state_dict'])

    model.to(device)
    model.eval()

    # Get image size
    image_size = model.get_input_size() if hasattr(model, 'get_input_size') else (224, 224)

    # Create dataloaders
    val_loader = create_test_dataloader(
        test_csv_path=val_csv_path,
        data_root=data_root,
        image_path_column=data_schema.image_path_column,
        primary_targets=config.primary_targets,
        image_size=image_size,
        batch_size=32,
        dataset_type=dataset_type,
        num_workers=0
    )

    test_loader = create_test_dataloader(
        test_csv_path=test_csv_path,
        data_root=data_root,
        image_path_column=data_schema.image_path_column,
        primary_targets=config.primary_targets,
        image_size=image_size,
        batch_size=32,
        dataset_type=dataset_type,
        num_workers=0
    )

    # Run inference
    val_pred_array = _run_inference(model, val_loader, device)
    test_pred_array = _run_inference(model, test_loader, device)

    # Cleanup
    del model, val_loader, test_loader
    cleanup_gpu_memory()

    return val_pred_array, test_pred_array


def process_fold_predictions(
    fold: int,
    val_data: pd.DataFrame,
    all_val_predictions: List[np.ndarray],
    all_test_predictions: List[np.ndarray],
    method: str,
    weights: Optional[List[float]],
    n_folds: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Combine fold predictions using ensemble method."""
    if not all_val_predictions or not all_test_predictions:
        logger.warning(f"No valid predictions for fold {fold}, skipping")
        return None, None

    ensembling_method = create_ensembling_method(method)

    # Combine predictions
    ensemble_val_pred = ensembling_method.combine(all_val_predictions, weights)
    ensemble_val_pred = np.clip(ensemble_val_pred, 0, None)

    ensemble_test_pred = ensembling_method.combine(all_test_predictions, weights)
    ensemble_test_pred = np.clip(ensemble_test_pred, 0, None)

    return ensemble_val_pred, ensemble_test_pred / n_folds


def process_single_fold_for_e2e_ensemble(
    fold: int,
    n_folds: int,
    train_df_with_folds: pd.DataFrame,
    model_paths: List[str],
    config,
    data_schema,
    val_csv_path: str,
    test_csv_path: str,
    data_root: str,
    device,
    method: str,
    weights: Optional[List[float]]
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], pd.Index]:
    """
    Process a single fold for end-to-end ensemble OOF generation.

    Args:
        fold: Fold number
        n_folds: Total number of folds
        train_df_with_folds: Training DataFrame with fold assignments
        model_paths: List of model paths
        config: Contest configuration
        data_schema: Contest data schema
        val_csv_path: Path to validation CSV
        test_csv_path: Path to test CSV
        data_root: Data root directory
        device: Training device
        method: Ensemble method
        weights: Model weights

    Returns:
        Tuple of (ensemble_val_pred, ensemble_test_pred, val_indices)
    """
    val_data = get_fold_data(train_df_with_folds, fold=fold, train=False)
    train_data = get_fold_data(train_df_with_folds, fold=fold, train=True)

    logger.info(f"  Train samples: {len(train_data)}")
    logger.info(f"  Val samples: {len(val_data)}")

    if len(val_data) == 0:
        logger.warning(f"  No validation data for fold {fold}, skipping")
        return None, None, pd.Index([])

    # Load all models and run inference
    all_val_predictions = []
    all_test_predictions = []

    for model_path in model_paths:
        val_pred, test_pred = load_and_run_model_inference(
            Path(model_path), config, data_schema, val_csv_path, test_csv_path, data_root, device
        )
        if val_pred is not None and test_pred is not None:
            all_val_predictions.append(val_pred)
            all_test_predictions.append(test_pred)

    # Combine predictions
    ensemble_val_pred, ensemble_test_pred = process_fold_predictions(
        fold, val_data, all_val_predictions, all_test_predictions, method, weights, n_folds
    )

    val_indices = val_data.index.values

    return ensemble_val_pred, ensemble_test_pred, val_indices
