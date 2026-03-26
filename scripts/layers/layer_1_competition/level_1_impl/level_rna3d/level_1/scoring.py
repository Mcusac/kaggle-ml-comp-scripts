"""RNA3D TM-score evaluation.

Implements a contest-appropriate TM-score for tuning/stacking:

- Kabsch rigid alignment between prediction and reference
- TM-score with standard d0(L) scaling
- Best-of-5 predictions per target
- Max over available reference conformations (x_1, x_2, ...) per target
- Mean over targets
"""
import numpy as np
import pandas as pd

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import group_labels_by_target


def _kabsch_align(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Align P onto Q using the Kabsch algorithm.

    Args:
        P: Predicted coordinates, shape (L, 3)
        Q: Reference coordinates, shape (L, 3)

    Returns:
        Aligned P, shape (L, 3)
    """
    if P.shape != Q.shape:
        raise ValueError(f"Kabsch alignment requires same shape, got {P.shape} vs {Q.shape}")

    P = np.asarray(P, dtype=np.float64)
    Q = np.asarray(Q, dtype=np.float64)

    Pc = P - P.mean(axis=0, keepdims=True)
    Qc = Q - Q.mean(axis=0, keepdims=True)

    C = Pc.T @ Qc

    V, S, Wt = np.linalg.svd(C)

    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1.0, 1.0, d])
    R = V @ D @ Wt

    aligned = Pc @ R
    aligned += Q.mean(axis=0, keepdims=True)
    return aligned.astype(np.float32)


def _tm_score(aligned: np.ndarray, reference: np.ndarray, d0: Optional[float] = None) -> float:
    """Compute TM-score between aligned prediction and reference.

    Args:
        aligned: Aligned prediction coordinates, shape (L, 3)
        reference: Reference coordinates, shape (L, 3)
        d0: Optional TM-score scaling factor. If None, computed from L.

    Returns:
        TM-score in [0, 1].
    """
    if aligned.shape != reference.shape:
        raise ValueError(f"TM-score requires same shape, got {aligned.shape} vs {reference.shape}")

    L = aligned.shape[0]
    if L <= 0:
        return 0.0

    if d0 is None:
        d0 = 1.24 * np.cbrt(L - 15.0) - 1.8
        if d0 < 0.5:
            d0 = 0.5

    diff = aligned.astype(np.float64) - reference.astype(np.float64)
    dist = np.linalg.norm(diff, axis=1)
    score = np.mean(1.0 / (1.0 + (dist / d0) ** 2))
    return float(score)


def _extract_reference_structures(labels: pd.DataFrame) -> Dict[str, List[np.ndarray]]:
    """Extract all reference conformations from labels per target_id.

    Each reference conformation is an (L, 3) array. Multiple conformations
    come from columns x_k,y_k,z_k.

    Args:
        labels: train/validation labels DataFrame.

    Returns:
        Dict mapping target_id -> list of reference arrays.
    """
    if labels.empty:
        return {}

    ks: List[int] = []
    for col in labels.columns:
        if col.startswith("x_"):
            try:
                k = int(col.split("_", 1)[1])
            except (IndexError, ValueError):
                continue
            y_col = f"y_{k}"
            z_col = f"z_{k}"
            if y_col in labels.columns and z_col in labels.columns:
                ks.append(k)
    ks = sorted(set(ks))
    if not ks:
        raise ValueError("No x_k/y_k/z_k coordinate columns found in labels.")

    groups = group_labels_by_target(labels)
    out: Dict[str, List[np.ndarray]] = {}
    for target_id, g in groups.items():
        refs: List[np.ndarray] = []
        for k in ks:
            cols = [f"x_{k}", f"y_{k}", f"z_{k}"]
            if not set(cols).issubset(g.columns):
                continue
            coords = g[cols].to_numpy(dtype=np.float32, copy=True)
            refs.append(coords)
        if refs:
            out[target_id] = refs

    return out


@dataclass(frozen=True)
class TargetTMScore:
    """Per-target TM-score breakdown."""

    target_id: str
    tm_score: float
    best_pred_index: int
    best_ref_index: int


def compute_target_tm_from_arrays(
    pred_coords: np.ndarray,
    ref_coords_list: Sequence[np.ndarray],
) -> TargetTMScore:
    """Compute best TM-score for a single target from arrays.

    Args:
        pred_coords: Prediction array shape (L, K, 3) where K is #predicted structures.
        ref_coords_list: List of reference arrays, each shape (L, 3).

    Returns:
        TargetTMScore with best TM-score and indices (prediction, reference).
    """
    if pred_coords.ndim != 3 or pred_coords.shape[2] != 3:
        raise ValueError(f"pred_coords must have shape (L, K, 3), got {pred_coords.shape}")
    L, K, _ = pred_coords.shape
    if not ref_coords_list:
        return TargetTMScore(target_id="", tm_score=0.0, best_pred_index=-1, best_ref_index=-1)

    best_score = 0.0
    best_pred_idx = -1
    best_ref_idx = -1

    for j in range(K):
        P = pred_coords[:, j, :]
        if P.shape != ref_coords_list[0].shape:
            raise ValueError(
                f"Prediction and reference must have same shape per target, "
                f"got {P.shape} vs {ref_coords_list[0].shape}"
            )
        for r_idx, Q in enumerate(ref_coords_list):
            aligned = _kabsch_align(P, Q)
            score = _tm_score(aligned, Q)
            if score > best_score:
                best_score = score
                best_pred_idx = j
                best_ref_idx = r_idx

    return TargetTMScore(
        target_id="",
        tm_score=best_score,
        best_pred_index=best_pred_idx,
        best_ref_index=best_ref_idx,
    )


def evaluate_predictions_tm(
    predictions: Mapping[str, np.ndarray],
    labels: pd.DataFrame,
    target_ids: Optional[Iterable[str]] = None,
) -> Tuple[float, Dict[str, TargetTMScore]]:
    """Evaluate predictions against labels using TM-score.

    Args:
        predictions: Mapping target_id -> prediction array (L, K, 3).
        labels: labels DataFrame containing at least ID,resid and x_k,y_k,z_k columns.
        target_ids: Optional subset of target_ids to evaluate. If None, use intersection
            between predictions keys and labels target_ids.

    Returns:
        (mean_tm_score, per_target_scores)
    """
    refs_by_target = _extract_reference_structures(labels)

    if target_ids is None:
        target_ids = sorted(set(predictions.keys()) & set(refs_by_target.keys()))
    else:
        target_ids = [tid for tid in target_ids if tid in predictions and tid in refs_by_target]

    per_target: Dict[str, TargetTMScore] = {}
    scores: List[float] = []

    for tid in target_ids:
        pred = predictions[tid]
        refs = refs_by_target[tid]
        t_result = compute_target_tm_from_arrays(pred, refs)
        per_target[tid] = TargetTMScore(
            target_id=tid,
            tm_score=t_result.tm_score,
            best_pred_index=t_result.best_pred_index,
            best_ref_index=t_result.best_ref_index,
        )
        scores.append(t_result.tm_score)

    mean_tm = float(np.mean(scores)) if scores else 0.0
    return mean_tm, per_target
