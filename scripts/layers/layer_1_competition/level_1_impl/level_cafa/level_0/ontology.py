"""CAFA 6 ontology system implementation."""

from typing import List, Dict, Any

from layers.layer_1_competition.level_0_infra.level_0 import ContestOntologySystem


class CAFAOntologySystem(ContestOntologySystem):
    """
    CAFA 6 ontology system for F/P/C (MFO/BPO/CCO).
    
    Implements the multi-task structure of CAFA where proteins can have
    annotations in three separate Gene Ontology aspects:
    - F (MFO): Molecular Function Ontology
    - P (BPO): Biological Process Ontology
    - C (CCO): Cellular Component Ontology
    """
    
    @property
    def ontology_codes(self) -> List[str]:
        """CAFA ontology codes."""
        from .constants import CAFA_ONTOLOGIES
        return list(CAFA_ONTOLOGIES)
    
    @property
    def ontology_names(self) -> Dict[str, str]:
        """CAFA ontology code to full name mapping."""
        return {
            'F': 'MFO',  # Molecular Function Ontology
            'P': 'BPO',  # Biological Process Ontology
            'C': 'CCO'   # Cellular Component Ontology
        }
    
    @property
    def ontology_full_names(self) -> Dict[str, str]:
        """CAFA ontology code to descriptive name mapping."""
        return {
            'F': 'Molecular Function',
            'P': 'Biological Process',
            'C': 'Cellular Component'
        }
    
    def get_ontology_config(self, ontology_code: str) -> Dict[str, Any]:
        """
        Get configuration for specific CAFA ontology.
        
        Args:
            ontology_code: Ontology code ('F', 'P', or 'C')
            
        Returns:
            Dict with ontology-specific configuration
            
        Raises:
            ValueError: If ontology_code is invalid
        """
        if not self.validate_ontology_code(ontology_code):
            raise ValueError(
                f"Invalid ontology code: {ontology_code}. "
                f"Must be one of {self.ontology_codes}"
            )
        
        return {
            'code': ontology_code,
            'name': self.ontology_names[ontology_code],
            'full_name': self.ontology_full_names[ontology_code],
            'description': f"Gene Ontology {self.ontology_full_names[ontology_code]} aspect",
            'hierarchical': True,  # All GO ontologies have hierarchical structure
        }
    
    def get_ontology_name(self, ontology_code: str) -> str:
        """
        Get ontology name from code.
        
        Args:
            ontology_code: Ontology code ('F', 'P', 'C')
            
        Returns:
            Ontology name ('MFO', 'BPO', 'CCO')
        """
        if not self.validate_ontology_code(ontology_code):
            raise ValueError(
                f"Invalid ontology code: {ontology_code}. "
                f"Must be one of {self.ontology_codes}"
            )
        return self.ontology_names[ontology_code]
    
    def get_ontology_code(self, ontology_name: str) -> str:
        """
        Get ontology code from name.
        
        Args:
            ontology_name: Ontology name ('MFO', 'BPO', 'CCO')
            
        Returns:
            Ontology code ('F', 'P', 'C')
        """
        name_to_code = {name: code for code, name in self.ontology_names.items()}
        if ontology_name not in name_to_code:
            raise ValueError(
                f"Invalid ontology name: {ontology_name}. "
                f"Must be one of {list(name_to_code.keys())}"
            )
        return name_to_code[ontology_name]
