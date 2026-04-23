"""Feature extraction for per-ontology training."""

import numpy as np

from typing import Dict, Any, List, Optional

from layers.layer_0_core.level_0 import get_logger, align_embeddings, HANDCRAFTED_FEATURE_DIM
from layers.layer_0_core.level_1 import fuse_embeddings
from layers.layer_0_core.level_2 import extract_handcrafted_features

from layers.layer_1_competition.level_1_impl.level_cafa.level_1 import load_embedding_data

_logger = get_logger(__name__)


class OntologyFeatureExtractor:
    """Extracts protein features for ontology training."""

    def extract_features(
        self,
        train_seqs: Dict[str, str],
        protein_ids: List[str],
        feature_type: str,
        ontology_config: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """
        Extract protein features.

        Supports hand-crafted features, embeddings, or fused features.

        Args:
            train_seqs: Dictionary mapping protein_id -> sequence
            protein_ids: List of protein IDs in training order
            feature_type: Feature type ('hand_crafted', 'embeddings', 'fused_embeddings')
            ontology_config: Ontology-specific configuration

        Returns:
            Feature matrix (N, feature_dim) or None if extraction fails
        """
        try:
            if feature_type == 'hand_crafted':
                return self._extract_handcrafted_features(train_seqs, protein_ids)
            elif feature_type in ['embeddings', 'fused_embeddings']:
                return self._extract_embedding_features(
                    train_seqs, protein_ids, feature_type, ontology_config
                )
            else:
                _logger.warning(f"Unknown feature type: {feature_type}, using hand-crafted")
                return self._extract_handcrafted_features(train_seqs, protein_ids)
        except Exception as e:
            _logger.error(f"Error extracting features: {e}")
            return None

    def _extract_handcrafted_features(
        self, train_seqs: Dict[str, str], protein_ids: List[str]
    ) -> np.ndarray:
        """Extract hand-crafted features."""
        try:
            features = []
            for pid in protein_ids:
                seq = train_seqs.get(pid, '')
                if seq:
                    feat = extract_handcrafted_features(seq)
                    features.append(feat)
                else:
                    features.append(np.zeros(HANDCRAFTED_FEATURE_DIM))

            X_train = np.array(features)
            _logger.info(f"Extracted {len(features)} hand-crafted feature vectors")
            return X_train
        except ImportError:
            _logger.warning(
                "Hand-crafted feature extraction not available. "
                "Using placeholder features."
            )
            return np.random.randn(len(protein_ids), HANDCRAFTED_FEATURE_DIM).astype(np.float32)

    def _extract_embedding_features(
        self,
        train_seqs: Dict[str, str],
        protein_ids: List[str],
        feature_type: str,
        ontology_config: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """Extract embedding features."""
        _logger.info(f"Extracting {feature_type} features...")

        if feature_type == 'fused_embeddings':
            features_list = ontology_config.get('features', ['protbert', 'esm2', 'hc'])

            embedding_list = []
            for feat_type in features_list:
                if feat_type == 'hc':
                    hc_features = []
                    for pid in protein_ids:
                        if pid in train_seqs:
                            feat = extract_handcrafted_features(train_seqs[pid])
                            hc_features.append(feat)
                        else:
                            hc_features.append(np.zeros(HANDCRAFTED_FEATURE_DIM, dtype=np.float32))
                    embedding_list.append((np.array(hc_features), protein_ids))
                else:
                    embeds, embed_ids = load_embedding_data(
                        embedding_type=feat_type,
                        datatype='train',
                        use_memmap=True
                    )
                    if len(embeds) > 0:
                        embedding_list.append((embeds, embed_ids))

            if embedding_list:
                fused, aligned_ids = fuse_embeddings(
                    embedding_list=embedding_list,
                    target_ids=protein_ids,
                    use_memmap=True
                )
                return fused
            else:
                _logger.warning("No embeddings loaded")
                return np.array([])
        else:
            embeds, embed_ids = load_embedding_data(
                embedding_type=feature_type,
                datatype='train',
                use_memmap=True
            )
            if len(embeds) > 0:
                aligned, _ = align_embeddings(embeds, embed_ids, protein_ids)
                return aligned
            else:
                _logger.warning(f"No embeddings loaded for {feature_type}")
                return np.array([])
