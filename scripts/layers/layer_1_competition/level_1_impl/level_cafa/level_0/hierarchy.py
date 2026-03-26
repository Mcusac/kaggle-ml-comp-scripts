"""CAFA 6 Gene Ontology hierarchy implementation."""

import numpy as np

from typing import Set, Dict, List
from pathlib import Path

from layers.layer_0_core.level_1 import HierarchyPropagator

from layers.layer_1_competition.level_0_infra.level_0 import ContestHierarchy


class CAFAHierarchy(ContestHierarchy):
    """
    CAFA 6 Gene Ontology hierarchy implementation.

    Manages the GO graph structure with is_a and part_of relationships.
    Provides ancestor/descendant lookups and label propagation.
    """

    def __init__(self):
        """Initialize CAFA hierarchy (empty until loaded from OBO file)."""
        self._propagator = HierarchyPropagator()

    def load_from_obo(self, obo_path: Path):
        """
        Load GO hierarchy from OBO file.

        Args:
            obo_path: Path to go-basic.obo file
        """
        self._propagator.load_from_obo(obo_path)
    
    def set_from_dicts(
        self,
        parents_map: Dict[str, Set[str]],
        children_map: Dict[str, Set[str]],
    ):
        """
        Set hierarchy from pre-parsed parent/child maps.

        Args:
            parents_map: Dict mapping term_id -> set of parent term_ids
            children_map: Dict mapping term_id -> set of child term_ids
        """
        self._propagator.set_from_dicts(parents_map, children_map)

    def get_ancestors(self, node_id: str) -> Set[str]:
        """Get all ancestor GO terms for a node."""
        return self._propagator.get_ancestors(node_id)

    def get_descendants(self, node_id: str) -> Set[str]:
        """Get all descendant GO terms for a node."""
        return self._propagator.get_descendants(node_id)

    def get_parents(self, node_id: str) -> Set[str]:
        """Get direct parent GO terms."""
        return self._propagator.get_parents(node_id)

    def get_children(self, node_id: str) -> Set[str]:
        """Get direct child GO terms."""
        return self._propagator.get_children(node_id)

    def propagate_predictions_batch(
        self,
        predictions: np.ndarray,
        term_ids: List[str],
        iterations: int = 3,
    ) -> np.ndarray:
        """Propagate predictions up GO hierarchy using max operation."""
        return self._propagator.propagate_predictions_batch(
            predictions, term_ids, iterations=iterations
        )
