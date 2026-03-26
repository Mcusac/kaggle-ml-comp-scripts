"""Contest ontology system abstract base class."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ContestOntologySystem(ABC):
    """
    Abstract base class for multi-task/ontology systems.

    Used for competitions with multiple independent task systems
    (e.g., CAFA with F/P/C ontologies for MFO/BPO/CCO).
    """

    @property
    @abstractmethod
    def ontology_codes(self) -> List[str]:
        """
        Return list of ontology codes.

        Example: ['F', 'P', 'C'] for CAFA MFO/BPO/CCO

        Returns:
            List of ontology codes
        """
        ...

    @property
    @abstractmethod
    def ontology_names(self) -> Dict[str, str]:
        """
        Return mapping of ontology codes to full names.

        Example: {'F': 'Molecular Function', 'P': 'Biological Process', 'C': 'Cellular Component'}

        Returns:
            Dict mapping code -> name
        """
        ...

    @abstractmethod
    def get_ontology_config(self, ontology_code: str) -> Dict[str, Any]:
        """
        Get configuration for specific ontology.

        Args:
            ontology_code: Ontology code (e.g., 'F', 'P', 'C')

        Returns:
            Dict with ontology-specific configuration
        """
        ...

    def validate_ontology_code(self, ontology_code: str) -> bool:
        """
        Validate ontology code.

        Args:
            ontology_code: Ontology code to validate

        Returns:
            True if valid, False otherwise
        """
        return ontology_code in self.ontology_codes
