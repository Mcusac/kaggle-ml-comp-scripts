"""GOA filtering utilities for CAFA post-processing."""

import pandas as pd

from pathlib import Path
from typing import Optional, Set

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import HierarchyPropagator

_logger = get_logger(__name__)


class GOAFilter:
    """Handles GOA negative annotation filtering."""

    def __init__(self, hierarchy_propagator: HierarchyPropagator):
        """
        Initialize GOA filter.

        Args:
            hierarchy_propagator: Hierarchy propagator for GO term operations
        """
        self.hierarchy_propagator = hierarchy_propagator

    def propagate_negative_annotations(
        self,
        goa_annotations_path: Path,
        go_obo_path: Path
    ) -> Set[str]:
        """Build set of negative protein-GO pairs from GOA annotations."""
        _logger.info("Building negative annotation set from GOA...")

        # Parse ontology (sets internal state for get_descendants)
        _logger.info("   [1/4] Parsing GO ontology structure...")
        self.hierarchy_propagator.parse_obo(go_obo_path)

        # Load GOA annotations
        _logger.info("   [2/4] Loading GOA annotations...")
        goa_file = self._find_goa_file(goa_annotations_path)

        if not goa_file:
            raise FileNotFoundError(f"GOA annotations file not found in {goa_annotations_path}")

        sep = '\t' if goa_file.suffix == '.tsv' else ','
        goa_df = pd.read_csv(goa_file, sep=sep, dtype=str)

        # Ensure required columns exist
        if len(goa_df.columns) >= 3:
            goa_df.columns = ['protein_id', 'go_term', 'qualifier'] + list(goa_df.columns[3:])

        # Filter negative annotations (NOT qualifiers)
        _logger.info("   [3/4] Extracting and propagating negative annotations...")
        negative_df = goa_df[goa_df['qualifier'].str.contains('NOT', na=False)].copy()
        negative_df = negative_df[['protein_id', 'go_term']].drop_duplicates()

        # Group by protein
        negative_dict = negative_df.groupby('protein_id')['go_term'].apply(list).to_dict()

        # Propagate negatives to descendants
        propagated = {}
        for protein_id, terms in negative_dict.items():
            neg_set = set(terms)
            for term in terms:
                # Add all descendants (hierarchy loaded by parse_obo)
                neg_set |= self.hierarchy_propagator.get_descendants(term)
            propagated[protein_id] = sorted(neg_set)

        # Convert to prediction keys
        _logger.info("   [4/4] Converting to prediction keys...")
        negative_keys = set()
        for protein_id, terms in propagated.items():
            for term in terms:
                negative_keys.add(f"{protein_id}_{term}")

        _logger.info(f"Total unique negative protein-GO pairs: {len(negative_keys):,}")
        return negative_keys

    def _find_goa_file(self, goa_annotations_path: Path) -> Optional[Path]:
        """Find GOA annotation file in directory."""
        for version in ["228", "227", "226"]:
            for ext in [".tsv", ".csv"]:
                candidate = goa_annotations_path / f'goa_uniprot_ver{version}{ext}'
                if candidate.exists():
                    return candidate
        return None

    def filter_submission_with_goa(
        self,
        submission_path: Path,
        negative_keys: Set[str],
        output_path: Path
    ) -> Path:
        """Filter submission file to remove negative annotations."""
        _logger.info(f"Filtering submission with {len(negative_keys):,} negative keys...")

        filtered_count = 0
        total_count = 0
        kept_count = 0

        with open(submission_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:

            for line in infile:
                total_count += 1
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    protein_id = parts[0]
                    go_term = parts[1]
                    pred_key = f"{protein_id}_{go_term}"

                    if pred_key not in negative_keys:
                        outfile.write(line)
                        kept_count += 1
                    else:
                        filtered_count += 1

        _logger.info(f"Filtered {filtered_count:,} / {total_count:,} predictions")
        _logger.info(f"Kept {kept_count:,} predictions ({kept_count/total_count*100:.2f}%)")

        return output_path
