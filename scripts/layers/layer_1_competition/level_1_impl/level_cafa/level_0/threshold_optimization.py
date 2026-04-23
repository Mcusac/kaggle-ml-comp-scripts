"""IA-weighted threshold optimization for CAFA 6 protein function prediction.

This module provides CAFA-specific threshold optimization using Information
Accretion (IA) weights for GO terms. IA-weighted F1 is critical for hierarchical
label spaces where different terms have different importance.
"""

import numpy as np
import pandas as pd

from typing import Dict, List, Tuple
from pathlib import Path

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def optimize_threshold_ia_weighted(
    y_val_proba: np.ndarray,
    y_val_true: np.ndarray,
    ia_weights: Dict[str, float],
    mlb,  # MultiLabelBinarizer with classes_ attribute
    threshold_grid: List[float],
    default_threshold: float = 0.5
) -> Tuple[float, float]:
    """
    Find optimal threshold by searching threshold grid and maximizing IA-weighted F1.
    
    Searches over threshold grid to find the threshold that maximizes IA-weighted F1 score.
    This is critical for hierarchical label spaces where different terms have different
    importance (IA weights).
    
    Args:
        y_val_proba: Validation prediction probabilities (n_samples, n_classes)
        y_val_true: True binary labels (n_samples, n_classes)
        ia_weights: Dictionary mapping GO term ID to IA weight
        mlb: MultiLabelBinarizer with classes_ attribute (must have classes_ attribute)
        threshold_grid: List of threshold values to search (e.g., [0.01, 0.02, ..., 0.50])
        default_threshold: Default threshold if no valid threshold found (default: 0.5)
        
    Returns:
        tuple: (best_threshold, best_f1_score)
        
    Notes:
        - IA-weighted F1 is critical for hierarchical label spaces (GO terms)
        - Grid search over thresholds is more reliable than optimization for discrete metrics
        - Threshold optimization improves F1 significantly (often 10-20% improvement)
    """
    best_threshold = default_threshold
    best_f1 = -1.0
    
    _logger.info(f"Searching {len(threshold_grid)} threshold values...")
    
    for threshold in threshold_grid:
        # Binarize predictions at this threshold
        y_pred_binary = (y_val_proba >= threshold).astype(int)
        
        # Compute IA-weighted F1
        _, _, f1 = _compute_ia_weighted_f1(y_val_true, y_pred_binary, ia_weights, mlb)
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    _logger.info(f"✓ Best threshold: {best_threshold:.3f}, Best IA-weighted F1: {best_f1:.6f}")
    
    return best_threshold, best_f1


def load_ia_weights(ia_file_path: Path) -> Dict[str, float]:
    """
    Load IA (Information Accretion) weights from IA.tsv file.
    
    Handles comma decimal separator (European format) and provides
    graceful error handling (returns empty dict if file not found).
    
    Args:
        ia_file_path: Path to IA.tsv file (contest-specific path)
        
    Returns:
        dict: Mapping from GO term ID to IA weight (float).
              Returns empty dict if file not found (graceful fallback).
    """
    if not ia_file_path.exists():
        _logger.warning(f"⚠️  IA file not found at {ia_file_path}, returning empty dict")
        return {}
    
    ia_weights = {}
    try:
        df = pd.read_csv(ia_file_path, sep='\t', header=None, names=['go', 'ia'], dtype=str)
        
        for _, row in df.iterrows():
            go_id = row['go']
            ia_str = row['ia']
            
            # Try to parse as float, handle comma decimal separator
            try:
                ia_weights[go_id] = float(ia_str)
            except ValueError:
                try:
                    # Try replacing comma with dot
                    ia_weights[go_id] = float(ia_str.replace(',', '.'))
                except ValueError:
                    # Default to 0.0 if parsing fails
                    ia_weights[go_id] = 0.0
        
        _logger.info(f"✓ Loaded {len(ia_weights):,} IA weights")
    except Exception as e:
        _logger.warning(f"⚠️  Error loading IA file: {e}, returning empty dict")
        return {}
    
    return ia_weights


def _compute_ia_weighted_f1(
    y_true: np.ndarray,
    y_pred_binary: np.ndarray,
    ia_weights: Dict[str, float],
    mlb  # MultiLabelBinarizer with classes_ attribute
) -> Tuple[float, float, float]:
    """
    Compute IA-weighted precision, recall, and F1 score.
    
    Args:
        y_true: True binary labels, shape (n_samples, n_classes)
        y_pred_binary: Predicted binary labels, shape (n_samples, n_classes)
        ia_weights: Dictionary mapping GO term ID to IA weight
        mlb: MultiLabelBinarizer with classes_ attribute
        
    Returns:
        tuple: (weighted_precision, weighted_recall, weighted_f1)
    """
    EPSILON_TINY = 1e-10
    
    # Compute per-class TP, FP, FN
    tp = ((y_true == 1) & (y_pred_binary == 1)).sum(axis=0).astype(float)
    fp = ((y_true == 0) & (y_pred_binary == 1)).sum(axis=0).astype(float)
    fn = ((y_true == 1) & (y_pred_binary == 0)).sum(axis=0).astype(float)
    
    # Compute per-class precision, recall, F1
    prec = tp / (tp + fp + EPSILON_TINY)
    rec = tp / (tp + fn + EPSILON_TINY)
    f1 = 2 * prec * rec / (prec + rec + EPSILON_TINY)
    
    # Get weights for each class (term)
    classes = mlb.classes_
    weights = np.array([ia_weights.get(c, 1.0) for c in classes], dtype=float)
    
    # Compute weighted averages
    weighted_f1 = (f1 * weights).sum() / (weights.sum() + EPSILON_TINY)
    weighted_prec = (prec * weights).sum() / (weights.sum() + EPSILON_TINY)
    weighted_rec = (rec * weights).sum() / (weights.sum() + EPSILON_TINY)
    
    return weighted_prec, weighted_rec, weighted_f1
