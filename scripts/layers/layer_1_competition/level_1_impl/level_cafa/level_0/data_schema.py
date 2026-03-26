"""CAFA 6 protein function prediction data schema."""

from typing import List

from layers.layer_1_competition.level_0_infra.level_0 import ContestDataSchema


class CAFADataSchema(ContestDataSchema):
    """
    CAFA 6 protein function prediction data schema.
    
    Defines data structure for CAFA competition with protein IDs and GO term annotations.
    """
    
    @property
    def sample_id_column(self) -> str:
        """CAFA sample ID column (protein ID)."""
        return 'EntryID'
    
    @property
    def target_columns(self) -> List[str]:
        """
        CAFA target columns (GO terms).
        
        In CAFA, targets are dynamic based on ontology and term set.
        This returns the generic term column name.
        """
        return ['term']
    
    @property
    def protein_id_column(self) -> str:
        """Protein identifier column."""
        return 'EntryID'
    
    @property
    def go_term_column(self) -> str:
        """GO term column name in train/test files."""
        return 'term'
    
    @property
    def aspect_column(self) -> str:
        """GO aspect/ontology column name."""
        return 'aspect'
    
    def validate_sample_id(self, sample_id: str) -> bool:
        """
        Validate CAFA protein ID format.
        
        Args:
            sample_id: Protein ID (e.g., 'A0A009EXK6')
            
        Returns:
            True if valid (non-empty string)
        """
        return isinstance(sample_id, str) and len(sample_id) > 0
    
    def validate_go_term(self, go_term: str) -> bool:
        """
        Validate GO term ID format.
        
        Args:
            go_term: GO term ID (e.g., 'GO:0003674')
            
        Returns:
            True if valid GO term format
        """
        if not isinstance(go_term, str):
            return False
        # GO terms should match pattern GO:NNNNNNN
        return go_term.startswith('GO:') and len(go_term) == 10 and go_term[3:].isdigit()
