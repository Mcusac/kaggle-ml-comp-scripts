"""Contest hierarchy abstract base class."""

import numpy as np

from abc import ABC, abstractmethod
from typing import List, Set


class ContestHierarchy(ABC):
    """
    Abstract base class for hierarchical target relationships.

    Used for competitions with hierarchical labels
    (e.g., CAFA with Gene Ontology graph).
    """

    @abstractmethod
    def get_ancestors(self, node_id: str) -> Set[str]:
        """
        Get all ancestor nodes of a given node.

        Args:
            node_id: Node identifier

        Returns:
            Set of ancestor node IDs
        """
        ...

    @abstractmethod
    def get_descendants(self, node_id: str) -> Set[str]:
        """
        Get all descendant nodes of a given node.

        Args:
            node_id: Node identifier

        Returns:
            Set of descendant node IDs
        """
        ...

    @abstractmethod
    def get_parents(self, node_id: str) -> Set[str]:
        """
        Get direct parent nodes.

        Args:
            node_id: Node identifier

        Returns:
            Set of parent node IDs
        """
        ...

    @abstractmethod
    def get_children(self, node_id: str) -> Set[str]:
        """
        Get direct child nodes.

        Args:
            node_id: Node identifier

        Returns:
            Set of child node IDs
        """
        ...

    def propagate_labels(self, labels: np.ndarray, label_ids: List[str]) -> np.ndarray:
        """
        Propagate labels up the hierarchy.

        If a node is labeled, all its ancestors should also be labeled.

        Args:
            labels: Binary label matrix (n_samples, n_labels)
            label_ids: List of label IDs corresponding to columns

        Returns:
            Propagated labels
        """
        propagated = labels.copy()

        for i, label_id in enumerate(label_ids):
            # For each sample where this label is positive
            positive_samples = labels[:, i] > 0
            if positive_samples.any():
                # Add all ancestors
                ancestors = self.get_ancestors(label_id)
                for ancestor in ancestors:
                    if ancestor in label_ids:
                        ancestor_idx = label_ids.index(ancestor)
                        propagated[positive_samples, ancestor_idx] = 1

        return propagated
