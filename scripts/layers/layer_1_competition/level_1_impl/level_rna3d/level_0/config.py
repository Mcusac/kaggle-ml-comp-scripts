"""Stanford RNA 3D Folding Part 2 contest configuration.

This contest is a structure prediction problem. The core framework's ContestConfig
interface is target/regression oriented, so this implementation intentionally keeps
the target interface minimal and uses identity derived-target behavior.
"""

from typing import Any, Dict, List

from layers.layer_1_competition.level_0_infra.level_0 import ContestConfig


class RNA3DConfig(ContestConfig):
    """
    Stanford RNA 3D Folding Part 2 configuration.

    Notes:
    - Submissions are 3D coordinates (x/y/z) for 5 predicted structures.
    - Scoring is TM-score (best-of-5 per target, averaged).
    - The framework's target-weight interface is not directly applicable here,
      so targets are left empty and derived targets are a no-op.
    """

    @property
    def target_weights(self) -> Dict[str, float]:
        """No target weights for coordinate submissions."""
        return {}

    @property
    def target_order(self) -> List[str]:
        """No ordered targets for coordinate submissions."""
        return []

    @property
    def primary_targets(self) -> List[str]:
        """No primary targets for coordinate submissions."""
        return []

    @property
    def derived_targets(self) -> List[str]:
        """No derived targets for coordinate submissions."""
        return []

    def compute_derived_targets(self, predictions: Any) -> Any:
        """Identity: no derived targets are computed."""
        return predictions
