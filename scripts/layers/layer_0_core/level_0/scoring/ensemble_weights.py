"""Contest ensembling utilities: weighted average and stacking weights."""

import numpy as np
from typing import Dict, List, Optional


def combine_predictions_weighted_average(
    predictions_list: List[Dict[str, np.ndarray]],
    weights: Optional[List[float]] = None,
) -> Dict[str, np.ndarray]:
    """
    Combine multiple prediction dicts via weighted average.

    Args:
        predictions_list: List of dicts mapping target_id -> prediction array.
        weights: Optional weights per model. Normalized if provided.

    Returns:
        Combined dict mapping target_id -> averaged array.

    Raises:
        ValueError: If predictions_list is empty.
    """
    if not predictions_list:
        raise ValueError("predictions_list cannot be empty")

    if weights is None:
        weights = [1.0 / len(predictions_list)] * len(predictions_list)
    else:
        total = sum(weights)
        weights = [w / total for w in weights]

    all_targets = set()
    for preds in predictions_list:
        all_targets.update(preds.keys())

    combined: Dict[str, np.ndarray] = {}
    for tid in all_targets:
        preds_with_tid = [p for p in predictions_list if tid in p]
        if not preds_with_tid:
            continue

        arrays = [p[tid] for p in preds_with_tid]
        wts = [weights[i] for i, p in enumerate(predictions_list) if tid in p]
        wts_sum = sum(wts)
        wts = [w / wts_sum for w in wts]

        combined_array = np.zeros_like(arrays[0], dtype=np.float32)
        for arr, w in zip(arrays, wts):
            combined_array += arr.astype(np.float32) * w
        combined[tid] = combined_array

    return combined


def fit_stacking_weights_from_scores(
    scores: np.ndarray,
    temperature: float = 2.0,
) -> np.ndarray:
    """
    Fit stacking weights from validation scores via softmax-like scaling.

    Args:
        scores: Per-model scores (higher is better).
        temperature: Scaling factor for exp (default 2.0).

    Returns:
        Normalized weights that sum to 1.
    """
    if len(scores) < 2:
        return np.ones(len(scores), dtype=np.float32) if len(scores) else np.array([])

    scores_array = np.asarray(scores, dtype=np.float32)
    min_s = scores_array.min()
    max_s = scores_array.max()
    spread = max_s - min_s + 1e-8
    normalized = (scores_array - min_s) / spread
    weights = np.exp(normalized * temperature)
    return (weights / weights.sum()).astype(np.float32)
