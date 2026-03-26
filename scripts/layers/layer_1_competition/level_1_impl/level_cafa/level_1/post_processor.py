"""CAFA 6 protein function prediction post-processing.

Refactored to use composition with helper classes:
  - HierarchyPropagator: GO hierarchy operations
  - GOAFilter: GOA negative annotation filtering
  - TsvSubmissionFormatter: Submission formatting and sorting
"""

import numpy as np

from pathlib import Path
from typing import Optional, Dict

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import HierarchyPropagator, TsvSubmissionFormatter

from layers.layer_1_competition.level_0_infra.level_0 import ContestPostProcessor

from layers.layer_1_competition.level_1_impl.level_cafa.level_0 import GOAFilter

logger = get_logger(__name__)


class CAFAPostProcessor(ContestPostProcessor):
    """
    CAFA 6 protein function prediction post-processor.
    
    Applies GO hierarchy propagation and probability calibration.
    Note: Full GO propagation requires hierarchy information loaded separately.
    """
    
    def __init__(self, threshold: float = 0.5):
        """
        Initialize CAFA post-processor.
        
        Args:
            threshold: Probability threshold for binary predictions (default: 0.5)
        """
        self.threshold = threshold
        self.hierarchy_propagator = HierarchyPropagator()
        self.goa_filter = GOAFilter(self.hierarchy_propagator)
        self.formatter = TsvSubmissionFormatter()
    
    def set_hierarchy(self, parents_map: Dict[str, set], term_to_idx: Dict[str, int]):
        """
        Set GO hierarchy information for propagation.
        
        Args:
            parents_map: Dict mapping GO term -> set of parent GO terms
            term_to_idx: Dict mapping GO term -> index in prediction array
        """
        self.hierarchy_propagator.set_hierarchy(parents_map, term_to_idx)
    
    def apply(self, predictions: np.ndarray) -> np.ndarray:
        """
        Apply post-processing to CAFA predictions.
        
        1. Clip probabilities to [0, 1]
        2. Apply GO hierarchy propagation if hierarchy loaded
        
        Args:
            predictions: Predictions array of shape (N, num_terms)
                        Values should be probabilities [0, 1]
            
        Returns:
            Post-processed predictions of shape (N, num_terms)
        """
        # Clip to valid probability range
        predictions = self.clip_values(predictions, min_val=0.0, max_val=1.0)
        
        # Apply GO hierarchy propagation if available
        if self.hierarchy_propagator.parents_map and self.hierarchy_propagator.term_to_idx:
            predictions = self._propagate_predictions(predictions)
        
        return predictions
    
    def apply_goa_filtering(
        self,
        submission_path: str,
        goa_annotations_path: str,
        go_obo_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Apply GOA negative propagation filtering to submission file.
        
        Filters predictions based on negative annotations from GOA database.
        Loads GOA annotations with NOT qualifiers, parses GO ontology structure,
        propagates negative annotations to all descendants, and filters submission
        to remove contradictory predictions.
        
        Args:
            submission_path: Path to raw submission TSV
            goa_annotations_path: Path to GOA annotations directory
            go_obo_path: Path to go-basic.obo file
            output_path: Optional output path (default: submission_path with '_filtered' suffix)
            
        Returns:
            Path to filtered submission
            
        Notes:
            - GOA filtering removes predictions that contradict known negatives
            - Can improve precision by removing false positives
            - Requires OBO file parsing and GO graph traversal
            - Graceful fallback if files not found (returns original path)
        """
        if output_path is None:
            output_path = str(Path(submission_path).with_suffix('')) + '_filtered.tsv'
        
        output_path = Path(output_path)
        submission_path = Path(submission_path)
        goa_annotations_path = Path(goa_annotations_path)
        go_obo_path = Path(go_obo_path)
        
        # Check if required files exist
        if not submission_path.exists():
            logger.warning(f"⚠️  Submission file not found: {submission_path}")
            return str(submission_path)
        
        if not go_obo_path.exists():
            logger.warning(f"⚠️  OBO file not found: {go_obo_path}, skipping GOA filtering")
            return str(submission_path)
        
        if not goa_annotations_path.exists():
            logger.warning(f"⚠️  GOA annotations not found: {goa_annotations_path}, skipping GOA filtering")
            return str(submission_path)
        
        try:
            # Build negative keys
            negative_keys = self.goa_filter.propagate_negative_annotations(goa_annotations_path, go_obo_path)
            
            # Filter submission
            filtered_path = self.goa_filter.filter_submission_with_goa(submission_path, negative_keys, output_path)
            
            logger.info(f"GOA filtering complete: {filtered_path}")
            return str(filtered_path)
        except Exception as e:
            logger.warning(f"GOA filtering failed: {e}, returning original submission")
            return str(submission_path)
    
    
    def enforce_prediction_limits(
        self,
        submission_path: str,
        max_predictions_per_protein: int = 1500,
        output_path: Optional[str] = None
    ) -> str:
        """
        Enforce maximum predictions per protein using heap-based top-K.
        
        Uses memory-efficient heap-based approach to keep only top-K predictions
        per protein. Groups predictions by protein, uses min-heap to maintain
        top-K highest-scoring predictions per protein.
        
        Args:
            submission_path: Path to submission TSV
            max_predictions_per_protein: Maximum predictions per protein (default: 1500)
            output_path: Optional output path
            
        Returns:
            Path to processed submission
        """
        return self.formatter.enforce_prediction_limits(
            submission_path, max_predictions_per_protein, output_path
        )
    
    def _sort_submission_external(
        self,
        input_path: str,
        output_path: str,
        chunk_size: int = 1000000
    ) -> None:
        """
        Sort submission file externally (for large files).
        
        Uses chunked sorting for files too large to fit in memory.
        Sorts file by (protein_id, term) using external merge sort.
        
        Args:
            input_path: Path to unsorted submission
            output_path: Path for sorted submission
            chunk_size: Number of lines per chunk (default: 1M)
        """
        self.formatter.sort_submission_external(input_path, output_path, chunk_size)
    
    def _propagate_predictions(self, predictions: np.ndarray) -> np.ndarray:
        """
        Propagate predictions up the GO hierarchy.
        
        If a child term has high probability, propagate to parent terms.
        Uses max operation: parent_prob = max(parent_prob, child_prob)
        
        Args:
            predictions: Predictions array of shape (N, num_terms)
            
        Returns:
            Propagated predictions of shape (N, num_terms)
        """
        propagated = predictions.copy()
        term_to_idx = self.hierarchy_propagator.term_to_idx
        
        # Create reverse mapping: index -> term
        idx_to_term = {idx: term for term, idx in term_to_idx.items()}
        
        # For each term, propagate its score to all ancestors
        for term_idx in range(predictions.shape[1]):
            term = idx_to_term.get(term_idx)
            if term is None:
                continue
            
            # Get all ancestors of this term
            ancestors = self.hierarchy_propagator.get_ancestors(term)
            
            # For each sample, propagate this term's score to its ancestors
            for ancestor in ancestors:
                ancestor_idx = term_to_idx.get(ancestor)
                if ancestor_idx is not None:
                    # Use max operation for propagation
                    propagated[:, ancestor_idx] = np.maximum(
                        propagated[:, ancestor_idx],
                        predictions[:, term_idx]
                    )
        
        return propagated
