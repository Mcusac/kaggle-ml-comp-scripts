"""CSIRO biomass competition post-processing."""

import numpy as np

from typing import Dict, Any, Optional

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import ContestPostProcessor

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import CSIROConfig

logger = get_logger(__name__)


class CSIROPostProcessor(ContestPostProcessor):
    """
    CSIRO biomass competition post-processor.
    
    Enforces physical constraints on predictions:
    1. GDM_g = Dry_Green_g + Dry_Clover_g
    2. Dry_Total_g = GDM_g + Dry_Dead_g
    
    Uses matrix projection to find the closest valid solution.
    """
    
    def __init__(self):
        """Initialize CSIRO post-processor with config."""
        self.config = CSIROConfig()
    
    def apply(
        self,
        predictions: np.ndarray,
        fixed_clover: bool = False,
        target_specific_rules: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> np.ndarray:
        """
        Apply post-processing to enforce CSIRO physical constraints.
        
        Args:
            predictions: Predictions array of shape (N, num_total_targets)
                        Columns in order: [Dry_Green_g, Dry_Clover_g, Dry_Dead_g, GDM_g, Dry_Total_g]
            fixed_clover: If True, keep Dry_Clover_g fixed and only adjust other targets.
                         Default: False (adjust all targets via projection)
            target_specific_rules: Optional dict mapping target names to post-processing rules.
                                  Example: {
                                      'Dry_Clover_g': {'multiplier': 0.8},
                                      'Dry_Dead_g': {'conditional_scale': {'threshold': 20, 'scale': 1.1}}
                                  }
            
        Returns:
            Post-processed predictions of shape (N, num_total_targets)
        """
        if predictions.ndim != 2 or predictions.shape[1] != self.config.num_total_targets:
            raise ValueError(
                f"Predictions array must be 2D with {self.config.num_total_targets} columns, "
                f"got shape {predictions.shape}"
            )
        
        # Apply target-specific rules first (before mass balance)
        if target_specific_rules:
            predictions = self._apply_target_specific_rules(predictions, target_specific_rules)
        
        # Transpose for matrix operations: Shape (num_total_targets, N)
        Y = predictions.T
        
        if fixed_clover:
            # Fixed-clover mode: Keep Dry_Clover_g fixed, adjust only other targets
            # Column indices: [0=Green, 1=Clover, 2=Dead, 3=GDM, 4=Total]
            clover_fixed = Y[1, :].copy()  # Dry_Clover_g is index 1
            
            # Adjust: GDM = Green + Clover_fixed
            Y[3, :] = Y[0, :] + clover_fixed  # GDM_g
            
            # Adjust: Total = GDM + Dead = Green + Clover_fixed + Dead
            Y[4, :] = Y[3, :] + Y[2, :]  # Dry_Total_g
            
            # Keep Green and Dead as is (or apply minimal adjustment if needed)
            # Clover stays fixed (already set)
            Y_reconciled = Y
        else:
            # Original method: adjust all targets via orthogonal projection
            # Get constraint matrix from config
            C = self.config.constraint_matrix
            
            # Project onto constraint subspace
            # Find Y_reconciled such that C @ Y_reconciled = 0 and minimizes ||Y_reconciled - Y||
            try:
                # Compute projection matrix: P = I - C^T @ (C @ C^T)^(-1) @ C
                CCt = C @ C.T
                inv_CCt = np.linalg.inv(CCt)
                P = np.eye(self.config.num_total_targets) - C.T @ inv_CCt @ C
                
                # Project: Y_reconciled = P @ Y
                Y_reconciled = P @ Y
                
            except np.linalg.LinAlgError:
                # Fallback to pseudo-inverse if matrix is singular
                logger.warning("Constraint matrix is singular, using pseudo-inverse")
                CCt = C @ C.T
                inv_CCt = np.linalg.pinv(CCt)
                P = np.eye(self.config.num_total_targets) - C.T @ inv_CCt @ C
                Y_reconciled = P @ Y
        
        # Transpose back: Shape (N, num_total_targets)
        Y_reconciled = Y_reconciled.T
        
        # Apply non-negative constraint (biomass cannot be negative)
        Y_reconciled = self.clip_values(Y_reconciled, min_val=0.0)
        
        # Additional corrections to ensure perfect consistency
        # (in case projection didn't perfectly satisfy constraints due to clipping)
        if not fixed_clover:
            Y_reconciled[:, 3] = Y_reconciled[:, 0] + Y_reconciled[:, 1]  # GDM_g
            Y_reconciled[:, 4] = Y_reconciled[:, 3] + Y_reconciled[:, 2]  # Dry_Total_g
        
        # Final clip to ensure non-negative
        Y_reconciled = np.clip(Y_reconciled, 0, None)
        
        return Y_reconciled
    
    def _apply_target_specific_rules(
        self,
        predictions: np.ndarray,
        rules: Dict[str, Dict[str, Any]]
    ) -> np.ndarray:
        """
        Apply target-specific post-processing rules.
        
        Args:
            predictions: Predictions array of shape (N, num_total_targets)
            rules: Dict mapping target names to rules. Supported rules:
                  - 'multiplier': Multiply predictions by a value
                  - 'conditional_scale': Scale if above/below threshold
                  - 'clip_min': Clip minimum value
        
        Returns:
            Modified predictions array
        """
        # Target column indices
        target_cols = ['Dry_Green_g', 'Dry_Clover_g', 'Dry_Dead_g', 'GDM_g', 'Dry_Total_g']
        target_idx = {name: i for i, name in enumerate(target_cols)}
        
        result = predictions.copy()
        
        for target_name, rule_dict in rules.items():
            if target_name not in target_idx:
                logger.warning(f"Unknown target name: {target_name}, skipping")
                continue
            
            idx = target_idx[target_name]
            
            # Apply multiplier
            if 'multiplier' in rule_dict:
                result[:, idx] *= rule_dict['multiplier']
            
            # Apply conditional scaling
            if 'conditional_scale' in rule_dict:
                cs = rule_dict['conditional_scale']
                threshold = cs.get('threshold', 0.0)
                scale = cs.get('scale', 1.0)
                condition = cs.get('condition', 'above')  # 'above' or 'below'
                
                if condition == 'above':
                    mask = result[:, idx] > threshold
                else:
                    mask = result[:, idx] < threshold
                
                result[mask, idx] *= scale
            
            # Apply clip minimum
            if 'clip_min' in rule_dict:
                result[:, idx] = np.maximum(result[:, idx], rule_dict['clip_min'])
        
        return result
