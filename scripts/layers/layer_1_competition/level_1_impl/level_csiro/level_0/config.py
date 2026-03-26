"""CSIRO biomass competition configuration."""

import numpy as np

from typing import Dict, List, Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestConfig

from .derived_targets import compute_derived_targets as _compute_derived_targets


class CSIROConfig(ContestConfig):
    """
    CSIRO biomass competition configuration.
    
    Defines target names, weights, and derived target computation for the
    CSIRO biomass prediction competition.
    """
    
    @property
    def target_weights(self) -> Dict[str, float]:
        """CSIRO target weights for weighted R² calculation."""
        return {
            'Dry_Green_g': 0.1,
            'Dry_Dead_g': 0.1,
            'Dry_Clover_g': 0.1,
            'GDM_g': 0.2,
            'Dry_Total_g': 0.5
        }
    
    @property
    def target_order(self) -> List[str]:
        """CSIRO target order (must match target_weights keys)."""
        return ['Dry_Green_g', 'Dry_Clover_g', 'Dry_Dead_g', 'GDM_g', 'Dry_Total_g']
    
    @property
    def primary_targets(self) -> List[str]:
        """CSIRO primary targets (model outputs 3 values)."""
        return ['Dry_Green_g', 'Dry_Clover_g', 'Dry_Dead_g']
    
    @property
    def derived_targets(self) -> List[str]:
        """CSIRO derived targets (computed from primary targets)."""
        return ['GDM_g', 'Dry_Total_g']

    @property
    def default_feature_extraction_model(self) -> str:
        """Default feature extraction model for CSIRO."""
        return 'dinov2_base'

    @property
    def default_batch_size(self) -> int:
        """Default batch size for CSIRO training."""
        return 32

    @property
    def default_n_folds(self) -> int:
        """Default number of CV folds for CSIRO."""
        return 5

    @property
    def default_image_size(self) -> tuple:
        """Default image size (fallback when model does not specify)."""
        return (224, 224)

    @property
    def constraint_matrix(self) -> Optional[np.ndarray]:
        """
        CSIRO constraint matrix for post-processing.
        
        Defines constraints:
        - GDM_g = Dry_Green_g + Dry_Clover_g
        - Dry_Total_g = GDM_g + Dry_Dead_g
        
        Order: [Dry_Green_g, Dry_Clover_g, Dry_Dead_g, GDM_g, Dry_Total_g]
        """
        return np.array([
            [-1, -1,  0,  1,  0],  # GDM_g = Dry_Green_g + Dry_Clover_g
            [ 0,  0, -1, -1,  1]   # Dry_Total_g = GDM_g + Dry_Dead_g
        ], dtype=float)
    
    def compute_derived_targets(self, predictions: np.ndarray) -> np.ndarray:
        """
        Compute CSIRO derived target values from primary target values.

        Takes predictions array with primary targets and appends derived targets.

        Args:
            predictions: Array of shape (N, 3) with primary targets
                        [Dry_Green_g, Dry_Clover_g, Dry_Dead_g]

        Returns:
            Array of shape (N, 5) with all targets
            [Dry_Green_g, Dry_Clover_g, Dry_Dead_g, GDM_g, Dry_Total_g]
        """
        return _compute_derived_targets(predictions)
