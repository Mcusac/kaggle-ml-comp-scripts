"""CAFA 6 protein function prediction configuration."""

import numpy as np

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import ContestConfig

_logger = get_logger(__name__)


class CAFAConfig(ContestConfig):
    """
    CAFA 6 protein function prediction configuration.
    
    This is a multi-label classification task with hierarchical Gene Ontology terms
    organized into three ontologies (F/P/C). Unlike CSIRO, there are no derived targets -
    each GO term is an independent binary classification target.
    """
    
    def __init__(self, ontology: str = 'F'):
        """
        Initialize CAFA config for a specific ontology.
        
        Args:
            ontology: Ontology code ('F', 'P', or 'C')
        """
        self.ontology = ontology
        # Target weights would come from term importance/frequency
        # For now, using uniform weights (can be customized per ontology)
        self._target_weights = {}
    
    @property
    def target_weights(self) -> Dict[str, float]:
        """
        CAFA target weights (GO terms).
        
        In CAFA, all GO terms are weighted equally for evaluation.
        Actual evaluation uses term-specific metrics.
        """
        # Return uniform weights - actual weights loaded from term data
        return self._target_weights if self._target_weights else {}
    
    @property
    def target_order(self) -> List[str]:
        """CAFA target order (GO term IDs)."""
        return list(self._target_weights.keys())
    
    @property
    def primary_targets(self) -> List[str]:
        """
        CAFA primary targets (all GO terms).
        
        In CAFA, there are no derived targets - all GO terms are primary.
        """
        return list(self._target_weights.keys())
    
    @property
    def derived_targets(self) -> List[str]:
        """
        CAFA derived targets (none).
        
        CAFA doesn't have derived targets like CSIRO.
        """
        return []
    
    def compute_derived_targets(self, predictions: np.ndarray) -> np.ndarray:
        """
        Compute derived targets (no-op for CAFA).
        
        CAFA has no derived targets, so this returns predictions unchanged.
        
        Args:
            predictions: Predictions array of shape (N, num_terms)
            
        Returns:
            Same predictions array unchanged
        """
        return predictions
    
    def set_target_weights_from_terms(self, go_terms: List[str], weights: Dict[str, float] = None):
        """
        Set target weights from list of GO terms.
        
        Args:
            go_terms: List of GO term IDs
            weights: Optional dict mapping GO term -> weight (default: uniform)
        """
        if weights is None:
            # Uniform weights
            self._target_weights = {term: 1.0 for term in go_terms}
        else:
            self._target_weights = {term: weights.get(term, 1.0) for term in go_terms}
    
    @property
    def per_ontology_hyperparams(self) -> Dict[str, Dict[str, Any]]:
        """
        Get per-ontology hyperparameters.
        
        Returns dictionary mapping ontology code ('F', 'P', 'C') to hyperparameter dict.
        Different ontologies may have different optimal hyperparameters.
        
        Returns:
            Dictionary mapping ontology -> hyperparameters dict
            
        Notes:
            - Per-ontology hyperparameters prevent confusion
            - Different ontologies have different optimal parameters
            - Should be defined in model config, not inferred
            - Default implementation returns empty dict (should be overridden in model configs)
        """
        return {}
    
    def get_ontology_hyperparams(self, ontology: str) -> Dict[str, Any]:
        """
        Get hyperparameters for a specific ontology.
        
        Args:
            ontology: Ontology code ('F', 'P', or 'C')
            
        Returns:
            Dictionary of hyperparameters for the ontology
            
        Raises:
            ValueError: If ontology not found in per_ontology_hyperparams
        """
        from .constants import validate_ontology
        validate_ontology(ontology)
        
        hyperparams = self.per_ontology_hyperparams
        
        if ontology in hyperparams:
            return hyperparams[ontology].copy()
        elif hyperparams:
            # If per-ontology hyperparams exist but this ontology is missing, raise error
            raise ValueError(
                f"Hyperparameters not found for ontology '{ontology}'. "
                f"Available ontologies: {list(hyperparams.keys())}"
            )
        else:
            # No per-ontology hyperparams defined, return empty dict
            _logger.warning(
                f"No per-ontology hyperparameters defined. "
                f"Returning empty dict for ontology '{ontology}'"
            )
            return {}
