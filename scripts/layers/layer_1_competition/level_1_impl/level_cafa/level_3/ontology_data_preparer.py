"""Data preparation helper for per-ontology training."""

import numpy as np
import pandas as pd

from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from sklearn.preprocessing import MultiLabelBinarizer

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_cafa.level_2 import OntologyFeatureExtractor

logger = get_logger(__name__)

_LABEL_PREP_ERRORS = (KeyError, ValueError, TypeError)


class OntologyDataPreparer:
    """Helper class for preparing features and labels from training data."""

    def __init__(self):
        self._feature_extractor = OntologyFeatureExtractor()

    def prepare_training_data(
        self,
        train_data: Dict[str, Any],
        ontology: str,
        ontology_config: Dict[str, Any]
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Prepare features and targets from training data.

        Args:
            train_data: Dictionary with 'sequences', 'terms', 'taxonomy', 'protein_ids'
            ontology: Ontology code
            ontology_config: Ontology-specific configuration

        Returns:
            Tuple of (X_train, y_train) or (None, None) if preparation fails
        """
        if train_data is None:
            return None, None

        train_seqs = train_data.get('sequences', {})
        train_terms = train_data.get('terms')
        protein_ids = train_data.get('protein_ids', [])

        if not train_seqs or train_terms is None or not protein_ids:
            logger.warning(f"Insufficient training data for {ontology} ontology")
            return None, None

        logger.info(f"Extracting features for {ontology} ontology...")
        feature_type = ontology_config.get('feature_type', 'hand_crafted')

        X_train = self._feature_extractor.extract_features(
            train_seqs=train_seqs,
            protein_ids=protein_ids,
            feature_type=feature_type,
            ontology_config=ontology_config
        )

        if X_train is None:
            logger.warning(f"Feature extraction failed for {ontology} ontology")
            return None, None

        logger.info(f"Extracted features shape: {X_train.shape}")

        logger.info(f"Preparing labels for {ontology} ontology...")
        y_train = self.prepare_labels(
            train_terms=train_terms,
            protein_ids=protein_ids,
            ontology=ontology,
            ontology_config=ontology_config
        )

        if y_train is None:
            logger.warning(f"Label preparation failed for {ontology} ontology")
            return None, None

        logger.info(f"Prepared labels shape: {y_train.shape}")

        return X_train, y_train

    def prepare_labels(
        self,
        train_terms: pd.DataFrame,
        protein_ids: List[str],
        ontology: str,
        ontology_config: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """
        Prepare multi-label binary matrix for ontology.

        Args:
            train_terms: DataFrame with protein, term, ontology columns
            protein_ids: List of protein IDs in training order
            ontology: Ontology code
            ontology_config: Ontology-specific configuration

        Returns:
            Binary label matrix (N, num_terms) or None if preparation fails
        """
        try:
            ont_terms = train_terms[train_terms['ontology'] == ontology]

            protein_terms = ont_terms.groupby('protein')['term'].apply(list).to_dict()

            top_k_labels = ontology_config.get('top_k_labels')
            if top_k_labels is not None and top_k_labels > 0:
                all_term_counts = Counter()
                for terms in protein_terms.values():
                    all_term_counts.update(terms)

                top_terms = set([term for term, _ in all_term_counts.most_common(top_k_labels)])
                logger.info(f"Restricting to top-{top_k_labels} most frequent GO terms ({len(top_terms)} unique)")

                filtered_protein_terms = {}
                for pid, terms in protein_terms.items():
                    filtered_protein_terms[pid] = [t for t in terms if t in top_terms]
                protein_terms = filtered_protein_terms

            labels_list = [protein_terms.get(pid, []) for pid in protein_ids]

            mlb = MultiLabelBinarizer(sparse_output=True)
            y_train = mlb.fit_transform(labels_list)

            if hasattr(y_train, 'toarray'):
                num_terms = y_train.shape[1]
                if num_terms < 10000:
                    y_train = y_train.toarray()
                else:
                    logger.info(f"Keeping labels as sparse matrix ({num_terms} terms)")

            logger.info(f"Prepared labels: {y_train.shape[0]} samples, {y_train.shape[1]} GO terms")

            return y_train
        except _LABEL_PREP_ERRORS as e:
            logger.error(f"Error preparing labels: {e}", exc_info=True)
            return None
