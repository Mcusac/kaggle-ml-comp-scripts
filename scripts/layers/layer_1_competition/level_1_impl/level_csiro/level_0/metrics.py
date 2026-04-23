"""CSIRO contest-specific evaluation metrics."""

import numpy as np

from typing import Optional, Tuple, Dict, Any

from layers.layer_0_core.level_0 import get_logger, Metric
from layers.layer_0_core.level_1 import register_metric
from layers.layer_0_core.level_2 import validate_paired_arrays
from layers.layer_0_core.level_3 import calculate_r2_per_target
from layers.layer_0_core.level_3 import calculate_weighted_r2_from_arrays, prepare_weighted_arrays

from .derived_targets import compute_derived_targets

_logger = get_logger(__name__)


# =====================================================
# CSIRO Constants
# =====================================================

NUM_PRIMARY_TARGETS = 3
NUM_TOTAL_TARGETS = 5

# Default target configuration (aligned with CSIROConfig.target_weights)
DEFAULT_TARGET_ORDER = [
    'Dry_Green_g',
    'Dry_Clover_g',
    'Dry_Dead_g',
    'GDM_g',
    'Dry_Total_g'
]

DEFAULT_TARGET_WEIGHTS = {
    'Dry_Green_g': 0.1,
    'Dry_Clover_g': 0.1,
    'Dry_Dead_g': 0.1,
    'GDM_g': 0.2,
    'Dry_Total_g': 0.5,
}


# =====================================================
# Core Calculation Functions
# =====================================================

def calculate_weighted_r2(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    weights: Optional[Dict[str, float]] = None,
    target_order: Optional[list] = None
) -> Tuple[float, np.ndarray]:
    """
    Calculate weighted R² score using CSIRO competition formula.
    
    Args:
        y_true: True values, shape (N, NUM_TOTAL_TARGETS) - all targets.
        y_pred: Predicted values, shape (N, NUM_TOTAL_TARGETS).
        weights: Dictionary mapping target names to weights.
                If None, uses equal weights.
        target_order: Ordered list of target names.
                     If None, uses default CSIRO target order.
        
    Returns:
        Tuple of (weighted_r2, r2_scores_per_target):
        - weighted_r2: Single weighted R² score (competition metric)
        - r2_scores_per_target: R² score for each target, shape (NUM_TOTAL_TARGETS,)
        
    Raises:
        ValueError: If input validation fails.
    """
    # Validate inputs
    validate_paired_arrays(y_true, y_pred)
    
    if y_true.shape[1] != NUM_TOTAL_TARGETS:
        raise ValueError(
            f"Expected {NUM_TOTAL_TARGETS} total targets, "
            f"got {y_true.shape[1]}"
        )
    
    # Use defaults if not provided
    if weights is None:
        weights = DEFAULT_TARGET_WEIGHTS
    if target_order is None:
        target_order = DEFAULT_TARGET_ORDER
    
    # Validate weights
    if not isinstance(weights, dict):
        raise TypeError(f"weights must be dict, got {type(weights)}")
    
    missing_keys = set(target_order) - set(weights.keys())
    if missing_keys:
        raise ValueError(f"weights missing required keys: {missing_keys}")
    
    # Prepare arrays
    y_true_flat, y_pred_flat, weights_flat = prepare_weighted_arrays(
        y_true, y_pred, weights, target_order
    )
    
    # Calculate weighted R²
    weighted_r2 = calculate_weighted_r2_from_arrays(
        y_true_flat, y_pred_flat, weights_flat
    )
    
    # Also calculate per-target R² for analysis
    r2_scores = calculate_r2_per_target(y_true, y_pred)
    
    return weighted_r2, r2_scores


def calculate_csiro_metric(
    outputs: np.ndarray,
    targets: np.ndarray,
    weights: Optional[Dict[str, float]] = None,
    target_order: Optional[list] = None
) -> Tuple[float, np.ndarray]:
    """
    Calculate weighted R² from primary target model outputs.
    
    Model outputs NUM_PRIMARY_TARGETS values (primary targets).
    Computes derived targets, then calculates weighted R².
    
    Args:
        outputs: Model predictions, shape (N, NUM_PRIMARY_TARGETS) - primary targets.
        targets: True values, shape (N, NUM_PRIMARY_TARGETS) - primary targets.
        weights: Optional target weights dict.
        target_order: Optional target order list.
        
    Returns:
        Tuple of (weighted_r2, r2_scores_per_target):
        - weighted_r2: Single weighted R² score
        - r2_scores_per_target: R² score for each target, shape (NUM_TOTAL_TARGETS,)
        
    Raises:
        ValueError: If input validation fails.
    """
    # Validate inputs
    validate_paired_arrays(outputs, targets)
    
    if outputs.shape[1] != NUM_PRIMARY_TARGETS:
        raise ValueError(
            f"Expected {NUM_PRIMARY_TARGETS} primary targets, "
            f"got {outputs.shape[1]}"
        )
    
    # Compute derived targets
    y_pred = compute_derived_targets(outputs)
    y_true = compute_derived_targets(targets)
    
    # Calculate weighted R²
    weighted_r2, r2_scores = calculate_weighted_r2(
        y_true, y_pred, weights, target_order
    )
    
    return weighted_r2, r2_scores


# =====================================================
# Metric Class
# =====================================================

class CSIROWeightedR2Metric(Metric):
    """
    CSIRO competition-specific weighted R² metric.
    
    Automatically handles computation of derived targets from primary targets.
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        target_order: Optional[list] = None
    ):
        """
        Initialize CSIRO metric.
        
        Args:
            weights: Target weights. If None, uses default equal weights.
            target_order: Target order. If None, uses default CSIRO order.
        """
        super().__init__("csiro_weighted_r2")
        self.weights = weights or DEFAULT_TARGET_WEIGHTS
        self.target_order = target_order or DEFAULT_TARGET_ORDER
    
    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate weighted R² and per-target R² scores.
        
        Args:
            y_true: True primary targets, shape (N, 3).
            y_pred: Predicted primary targets, shape (N, 3).
            
        Returns:
            Dictionary containing:
            - 'weighted_r2': Overall competition score
            - 'r2_per_target': Array of per-target R² scores
        """
        # Override with kwargs if provided
        weights = kwargs.get("weights", self.weights)
        target_order = kwargs.get("target_order", self.target_order)
        
        weighted_r2, r2_scores = calculate_csiro_metric(
            y_pred, y_true, weights, target_order
        )
        
        return {
            "weighted_r2": weighted_r2,
            "r2_per_target": r2_scores
        }


# =====================================================
# Auto-register metric
# =====================================================

register_metric(CSIROWeightedR2Metric())


# =====================================================
# Config-aware wrapper (orchestration interface)
# =====================================================

def calc_metric(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    config: Optional[Any] = None,
    weights: Optional[Dict[str, float]] = None,
    target_order: Optional[list] = None
) -> Tuple[float, np.ndarray]:
    """
    CSIRO metric interface: (predictions, targets, config) -> (weighted_r2, r2_scores).

    config may have .evaluation or be a dict with weights/target_order.
    """
    if weights is None or target_order is None:
        eval_cfg = None
        if config is not None:
            eval_cfg = getattr(config, "evaluation", None) or (
                config if isinstance(config, dict) else None
            )
        if eval_cfg is not None:
            if weights is None:
                weights = getattr(eval_cfg, "weights", None) or (
                    eval_cfg.get("weights") if isinstance(eval_cfg, dict) else None
                )
            if target_order is None:
                target_order = getattr(eval_cfg, "target_order", None) or (
                    eval_cfg.get("target_order") if isinstance(eval_cfg, dict) else None
                )
    return calculate_csiro_metric(
        y_pred, y_true, weights=weights, target_order=target_order
    )
