"""Chunked model prediction for memory-efficient inference on large datasets."""

import gc
import numpy as np

from typing import Callable, List, Optional

from level_0 import get_logger

logger = get_logger(__name__)


def _dispatch_predict(model, X: np.ndarray) -> np.ndarray:
    """Dispatch prediction to predict_proba or predict depending on model interface."""
    if hasattr(model, 'predict_proba'):
        return model.predict_proba(X)
    if hasattr(model, 'predict'):
        return model.predict(X)
    raise ValueError("Model must have predict_proba() or predict() method")


def predict_in_chunks(
    model,
    X: np.ndarray,
    batch_size: int = 1000,
    progress_interval: int = 100,
) -> np.ndarray:
    """
    Make predictions in chunks for memory efficiency.

    Processes predictions in batches to avoid OOM on large test sets.

    Args:
        model: Trained model with predict_proba or predict method.
        X: Feature matrix of shape (n_samples, n_features).
        batch_size: Number of samples per prediction batch (default: 1000).
        progress_interval: Log progress every N batches (default: 100).

    Returns:
        Predictions array of shape (n_samples, n_targets).
    """
    n_samples = len(X)
    total_batches = (n_samples + batch_size - 1) // batch_size
    predictions_list = []

    logger.info(
        f"Making predictions in chunks "
        f"(batch_size={batch_size:,}, total_samples={n_samples:,})..."
    )

    for i in range(0, n_samples, batch_size):
        batch_num = (i // batch_size) + 1
        batch_preds = _dispatch_predict(model, X[i:i + batch_size])
        predictions_list.append(batch_preds)

        if batch_num % progress_interval == 0 or batch_num == total_batches:
            logger.info(
                f"  Processed {min(i + batch_size, n_samples):,}/{n_samples:,} samples "
                f"({batch_num}/{total_batches} batches)"
            )

    predictions = np.vstack(predictions_list)
    logger.info(f"✓ Completed predictions: shape {predictions.shape}")
    return predictions


def predict_proteins_in_chunks(
    model,
    protein_ids: List[str],
    feature_extractor: Callable,
    batch_size: int = 3000,
    output_file: Optional[str] = None,
    format_prediction_row: Optional[Callable] = None,
    progress_interval: int = 10,
) -> Optional[np.ndarray]:
    """
    Make predictions for proteins in chunks (protein-level batching).

    Processes proteins in batches to prevent OOM on large test sets:
    1. Extracts features for the batch via the injected feature_extractor.
    2. Makes predictions for the batch.
    3. Writes to file immediately (if output_file provided), then deletes
       the prediction matrix to free memory.

    Args:
        model: Trained model with predict_proba or predict method.
        protein_ids: List of protein IDs to predict for.
        feature_extractor: Callable(protein_ids) -> (features, aligned_ids).
        batch_size: Number of proteins per batch (default: 3000).
        output_file: Optional path to write predictions incrementally.
            If provided, the caller must also supply format_prediction_row.
            Returns None when this is set.
        format_prediction_row: Callable(protein_id, prediction_row) -> str.
            Required when output_file is provided. Formats a single protein's
            predictions as a line to write.
        progress_interval: Log progress every N batches (default: 10).

    Returns:
        Predictions array of shape (n_proteins, n_targets) if output_file is
        None. Returns None if output_file is provided (predictions written
        to disk incrementally).

    Raises:
        ValueError: If output_file is provided but format_prediction_row is not.
    """
    if output_file is not None and format_prediction_row is None:
        raise ValueError(
            "format_prediction_row is required when output_file is provided"
        )

    n_proteins = len(protein_ids)
    total_batches = (n_proteins + batch_size - 1) // batch_size

    logger.info(
        f"Making protein-level predictions in chunks "
        f"(batch_size={batch_size:,}, total_proteins={n_proteins:,})..."
    )

    all_predictions: Optional[List[np.ndarray]] = [] if output_file is None else None
    output_handle = None

    if output_file:
        output_handle = open(output_file, 'w')
        logger.info(f"Writing predictions incrementally to {output_file}")

    try:
        for batch_idx in range(0, n_proteins, batch_size):
            batch_protein_ids = protein_ids[batch_idx:batch_idx + batch_size]
            batch_num = (batch_idx // batch_size) + 1

            batch_features, aligned_ids = feature_extractor(batch_protein_ids)
            batch_preds = _dispatch_predict(model, batch_features)

            if output_handle is not None:
                for i, protein_id in enumerate(aligned_ids):
                    output_handle.write(
                        format_prediction_row(protein_id, batch_preds[i])
                    )
                del batch_preds
                gc.collect()
            else:
                all_predictions.append(batch_preds)

            del batch_features

            if batch_num % progress_interval == 0 or batch_num == total_batches:
                logger.info(
                    f"  Processed "
                    f"{min(batch_idx + batch_size, n_proteins):,}/{n_proteins:,} proteins "
                    f"({batch_num}/{total_batches} batches)"
                )

        if output_handle:
            logger.info(
                f"✓ Completed predictions: {n_proteins:,} proteins written to {output_file}"
            )
            return None

        predictions = np.vstack(all_predictions)
        logger.info(f"✓ Completed predictions: shape {predictions.shape}")
        return predictions

    finally:
        if output_handle:
            output_handle.close()