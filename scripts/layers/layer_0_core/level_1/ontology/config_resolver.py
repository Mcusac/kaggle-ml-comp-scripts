"""Generic per-ontology config resolution for multi-ontology contests."""

from typing import Any, Dict


class OntologyConfigResolver:
    """
    Resolve per-ontology configuration by merging base config with ontology overrides.

    Use for contests with multiple ontologies (e.g. F, P, C) where each
    has different hyperparameters.
    """

    def get_ontology_config(
        self, ontology: str, base_config: Any
    ) -> Dict[str, Any]:
        """
        Get configuration for a specific ontology.

        Merges base config with per-ontology overrides from
        base_config.per_ontology_hyperparams if present.

        Args:
            ontology: Ontology code (e.g. 'F', 'P', 'C')
            base_config: Base configuration object

        Returns:
            Configuration dict with ontology-specific values merged in
        """
        base_dict = (
            base_config.__dict__.copy()
            if hasattr(base_config, "__dict__")
            else {}
        )
        if hasattr(base_config, "per_ontology_hyperparams"):
            per_ontology = getattr(base_config, "per_ontology_hyperparams", {})
            ont_hyperparams = per_ontology.get(ontology, {})
            base_dict.update(ont_hyperparams)
        return base_dict
