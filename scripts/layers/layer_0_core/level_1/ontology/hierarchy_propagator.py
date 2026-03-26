"""Generic hierarchy propagation for ontology graphs."""

import numpy as np
from pathlib import Path
from typing import Dict, List, Set, Tuple

from level_0 import parse_obo_file


def _build_children_from_parents(
    parents_map: Dict[str, Set[str]],
) -> Dict[str, Set[str]]:
    """Build children map from parents map."""
    from collections import defaultdict

    children: Dict[str, Set[str]] = defaultdict(set)
    for child, parents in parents_map.items():
        for parent in parents:
            children[parent].add(child)
    return dict(children)


class HierarchyPropagator:
    """
    Generic hierarchy propagator for ontology graphs.

    Handles parent/child relationships, ancestor/descendant lookups,
    and prediction propagation up the hierarchy.
    """

    def __init__(
        self,
        parents_map: Dict[str, Set[str]] | None = None,
        children_map: Dict[str, Set[str]] | None = None,
        term_to_idx: Dict[str, int] | None = None,
    ):
        """
        Initialize with parent/child maps.

        Args:
            parents_map: term_id -> set of parent term_ids
            children_map: term_id -> set of child term_ids (built from parents_map if None)
            term_to_idx: Optional mapping of term_id -> column index for propagation
        """
        self._parents_map = parents_map or {}
        self._children_map = children_map or (
            _build_children_from_parents(self._parents_map) if self._parents_map else {}
        )
        self._ancestors_cache: Dict[str, Set[str]] = {}
        self._descendants_cache: Dict[str, Set[str]] = {}
        self.parents_map = self._parents_map
        self.term_to_idx = term_to_idx or {}

    def load_from_obo(self, obo_path: Path) -> None:
        """Load hierarchy from OBO file."""
        self._parents_map, self._children_map = parse_obo_file(obo_path)
        self.parents_map = self._parents_map
        self._ancestors_cache = {}
        self._descendants_cache = {}

    def parse_obo(self, obo_path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        """Parse OBO file and set internal state. Returns (parents_map, children_map)."""
        self._parents_map, self._children_map = parse_obo_file(obo_path)
        self.parents_map = self._parents_map
        self._ancestors_cache = {}
        self._descendants_cache = {}
        return self._parents_map, self._children_map

    def set_hierarchy(
        self,
        parents_map: Dict[str, Set[str]],
        term_to_idx: Dict[str, int],
    ) -> None:
        """Set hierarchy from parent map and term-to-index mapping."""
        self.parents_map = parents_map
        self.term_to_idx = term_to_idx
        children_map = _build_children_from_parents(parents_map)
        self.set_from_dicts(parents_map, children_map)

    def set_from_dicts(
        self,
        parents_map: Dict[str, Set[str]],
        children_map: Dict[str, Set[str]],
    ) -> None:
        """Set hierarchy from pre-parsed maps."""
        self._parents_map = parents_map
        self._children_map = children_map
        self.parents_map = parents_map
        self._ancestors_cache = {}
        self._descendants_cache = {}

    def get_ancestors(self, node_id: str) -> Set[str]:
        """Get all ancestor nodes (transitive closure)."""
        if node_id in self._ancestors_cache:
            return self._ancestors_cache[node_id]
        ancestors: Set[str] = set()
        stack = [node_id]
        while stack:
            current = stack.pop()
            for parent in self._parents_map.get(current, set()):
                if parent not in ancestors:
                    ancestors.add(parent)
                    stack.append(parent)
        self._ancestors_cache[node_id] = ancestors
        return ancestors

    def get_descendants(self, node_id: str) -> Set[str]:
        """Get all descendant nodes (transitive closure)."""
        if node_id in self._descendants_cache:
            return self._descendants_cache[node_id]
        descendants: Set[str] = set()
        stack = [node_id]
        while stack:
            current = stack.pop()
            for child in self._children_map.get(current, set()):
                if child not in descendants:
                    descendants.add(child)
                    stack.append(child)
        self._descendants_cache[node_id] = descendants
        return descendants

    def get_parents(self, node_id: str) -> Set[str]:
        """Get direct parent nodes."""
        return self._parents_map.get(node_id, set())

    def get_children(self, node_id: str) -> Set[str]:
        """Get direct child nodes."""
        return self._children_map.get(node_id, set())

    def propagate_predictions_batch(
        self,
        predictions: np.ndarray,
        term_ids: List[str],
        iterations: int = 3,
    ) -> np.ndarray:
        """
        Propagate predictions up the hierarchy using max operation.

        Child scores propagate to ancestors; parent gets max of its score
        and all descendant scores.

        Args:
            predictions: (n_samples, n_terms) probability matrix
            term_ids: List of term IDs corresponding to columns
            iterations: Number of propagation passes

        Returns:
            Propagated predictions (n_samples, n_terms)
        """
        if not term_ids or len(term_ids) != predictions.shape[1]:
            raise ValueError(
                f"term_ids length ({len(term_ids)}) must match predictions columns ({predictions.shape[1]})"
            )
        term_to_idx = {term: idx for idx, term in enumerate(term_ids)}
        propagated = predictions.copy()
        for _ in range(iterations):
            for term_idx, term_id in enumerate(term_ids):
                ancestors = self.get_ancestors(term_id)
                for ancestor_id in ancestors:
                    ancestor_idx = term_to_idx.get(ancestor_id)
                    if ancestor_idx is not None:
                        propagated[:, ancestor_idx] = np.maximum(
                            propagated[:, ancestor_idx],
                            predictions[:, term_idx],
                        )
            predictions = propagated.copy()
        return propagated
