"""CSIRO competition-specific ensemble implementations.

This module provides ensemble methods pre-configured with CSIRO competition
target variables. These are convenience wrappers around the generic ensemble
methods from level_1.

CSIRO Targets:
- Dry_Green_g: Dry green material (grams)
- Dry_Clover_g: Dry clover (grams)
- Dry_Dead_g: Dry dead material (grams)
- GDM_g: Green dry matter (grams)
- Dry_Total_g: Total dry material (grams)
"""

import numpy as np

from typing import Dict, List, Optional

from layers.layer_0_core.level_0 import get_logger, EnsemblingMethod
from layers.layer_0_core.level_3 import PerTargetWeightedEnsemble
from layers.layer_0_core.level_6 import TargetSpecificEnsemble


logger = get_logger(__name__)

# =============================================================================
# CSIRO-SPECIFIC CONSTANTS
# =============================================================================

# Target names for CSIRO competition (in order)
CSIRO_TARGET_NAMES = [
    'Dry_Green_g',
    'Dry_Clover_g',
    'Dry_Dead_g',
    'GDM_g',
    'Dry_Total_g'
]


# =============================================================================
# CSIRO ENSEMBLE WRAPPERS
# =============================================================================

class CSIROTargetSpecificEnsemble(EnsemblingMethod):
    """
    CSIRO-specific target selection ensemble.
    
    Allows selecting which base model to use for each CSIRO target variable.
    Pre-configured with CSIRO target names.
    
    Args:
        target_selection: Dict mapping CSIRO target name to model index.
                         Example: {'Dry_Green_g': 0, 'Dry_Total_g': 2}
        base_method: Base ensemble method for non-overridden targets.
                    Defaults to WeightedAverageEnsemble if None.
    
    Example:
        >>> selection = {'Dry_Green_g': 0, 'GDM_g': 2}
        >>> ensemble = CSIROTargetSpecificEnsemble(selection)
        >>> result = ensemble.combine(predictions, weights=scores)
    """

    def __init__(
        self,
        target_selection: Dict[str, int],
        base_method: Optional[EnsemblingMethod] = None
    ):
        """
        Initialize CSIRO target-specific ensemble.
        
        Args:
            target_selection: Mapping of CSIRO target name to model index.
            base_method: Base ensemble method for other targets.
        """
        # Validate that all target names are valid CSIRO targets
        for target_name in target_selection.keys():
            if target_name not in CSIRO_TARGET_NAMES:
                logger.warning(
                    f"Target '{target_name}' is not a known CSIRO target. "
                    f"Known targets: {CSIRO_TARGET_NAMES}"
                )
        
        # Create generic ensemble with CSIRO target names
        self._ensemble = TargetSpecificEnsemble(
            target_selection=target_selection,
            target_names=CSIRO_TARGET_NAMES,
            base_method=base_method
        )

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Combine predictions using CSIRO target-specific model selection.
        
        Args:
            predictions_list: List of prediction arrays, each shape (n_samples, 5).
                             Columns correspond to CSIRO_TARGET_NAMES in order.
            weights: Weights for base ensemble method.
            
        Returns:
            Combined predictions with specified targets replaced by selected models.
            Shape: (n_samples, 5)
        """
        return self._ensemble.combine(predictions_list, weights)

    def get_name(self) -> str:
        return 'csiro_target_specific'


class CSIROPerTargetWeightedEnsemble(EnsemblingMethod):
    """
    CSIRO-specific per-target weighted ensemble.
    
    Different weights for each CSIRO target variable.
    Pre-configured with CSIRO target names.
    
    Args:
        per_target_weights: Dict mapping CSIRO target name to weights list.
                           Example: {
                               'Dry_Green_g': [0.3, 0.7],
                               'GDM_g': [0.5, 0.5]
                           }
    
    Example:
        >>> weights_by_target = {
        ...     'Dry_Green_g': [0.2, 0.8],
        ...     'GDM_g': [0.6, 0.4]
        ... }
        >>> ensemble = CSIROPerTargetWeightedEnsemble(weights_by_target)
        >>> result = ensemble.combine(predictions)
    """

    def __init__(self, per_target_weights: Dict[str, List[float]]):
        """
        Initialize CSIRO per-target weighted ensemble.
        
        Args:
            per_target_weights: Dict mapping CSIRO target name to weights list.
        """
        # Validate that all target names are valid CSIRO targets
        for target_name in per_target_weights.keys():
            if target_name not in CSIRO_TARGET_NAMES:
                logger.warning(
                    f"Target '{target_name}' is not a known CSIRO target. "
                    f"Known targets: {CSIRO_TARGET_NAMES}"
                )
        
        # Create generic ensemble with CSIRO target names
        self._ensemble = PerTargetWeightedEnsemble(
            per_target_weights=per_target_weights,
            target_names=CSIRO_TARGET_NAMES
        )

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Combine predictions using CSIRO per-target weights.
        
        Args:
            predictions_list: List of prediction arrays, each shape (n_samples, 5).
                             Columns correspond to CSIRO_TARGET_NAMES in order.
            weights: Not used by this method (ignored if provided).
            
        Returns:
            Combined predictions with per-target weights applied.
            Shape: (n_samples, 5)
        """
        return self._ensemble.combine(predictions_list, weights)

    def get_name(self) -> str:
        return 'csiro_per_target_weighted'
