"""Data loading helper for per-ontology training."""

import pandas as pd

from typing import Dict, Any, Optional, Tuple, Type
from Bio import SeqIO

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import normalize_protein_id

_logger = get_logger(__name__)

_EXPECTED_IO_ERRORS: Tuple[Type[BaseException], ...] = (
    OSError,
    pd.errors.EmptyDataError,
    pd.errors.ParserError,
    KeyError,
)


class OntologyDataLoader:
    """Helper class for loading ontology-specific training data."""

    def load_training_data(self, ontology: str, paths, data_schema) -> Optional[Dict[str, Any]]:
        """
        Load training data filtered by ontology.

        CAFA uses TSV files: train_terms.tsv and train_sequences.fasta

        Args:
            ontology: Ontology code
            paths: Contest paths instance
            data_schema: Contest data schema

        Returns:
            Dictionary with 'sequences', 'terms', 'taxonomy' keys, or None if not available
        """
        data_root = paths.get_data_root()
        train_dir = data_root / 'Train'

        if not train_dir.exists():
            _logger.warning(f"Training directory not found: {train_dir}")
            return None

        train_terms_path = train_dir / 'train_terms.tsv'
        if not train_terms_path.exists():
            _logger.warning(f"Training terms file not found: {train_terms_path}")
            return None

        train_seqs_path = train_dir / 'train_sequences.fasta'
        if not train_seqs_path.exists():
            _logger.warning(f"Training sequences file not found: {train_seqs_path}")
            return None

        try:
            train_terms = pd.read_csv(
                train_terms_path, sep='\t', names=['protein', 'term', 'ontology']
            )

            ont_terms = train_terms[train_terms['ontology'] == ontology]
            _logger.info(f"Loaded {len(ont_terms)} term annotations for {ontology} ontology")

            target_proteins = set(ont_terms['protein'].unique())
            _logger.info(f"Found {len(target_proteins)} unique proteins for {ontology} ontology")

            train_seqs = {}
            for rec in SeqIO.parse(train_seqs_path, 'fasta'):
                pid = normalize_protein_id(rec.id)
                if pid in target_proteins:
                    train_seqs[pid] = str(rec.seq)

            _logger.info(f"Loaded {len(train_seqs)} sequences for {ontology} ontology")

            train_taxonomy = None
            train_taxonomy_path = train_dir / 'train_taxonomy.tsv'
            if train_taxonomy_path.exists():
                train_taxonomy = pd.read_csv(
                    train_taxonomy_path, sep='\t', names=['protein', 'taxon']
                )
                _logger.info(f"Loaded taxonomy for {len(train_taxonomy)} proteins")

            return {
                'sequences': train_seqs,
                'terms': ont_terms,
                'taxonomy': train_taxonomy,
                'protein_ids': sorted(list(target_proteins))
            }
        except _EXPECTED_IO_ERRORS as e:
            _logger.error(
                f"Error loading training data for {ontology}: {e}",
                exc_info=True,
            )
            return None
