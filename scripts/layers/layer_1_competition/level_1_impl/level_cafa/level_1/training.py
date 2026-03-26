"""
CAFA-specific training configuration.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

from layers.layer_0_core.level_2 import MultiTaskTrainingConfig

from layers.layer_1_competition.level_1_impl.level_cafa.level_0 import CAFA_ONTOLOGIES


@dataclass
class CAFATrainingConfig(MultiTaskTrainingConfig):
    """
    CAFA training configuration.

    Provides ontology-aware hyperparameter overrides.
    """

    # ontology_code -> overrides
    per_ontology_hyperparams: Optional[
        Dict[str, Dict[str, Any]]
    ] = None


    def __post_init__(self):
        """
        Validate ontology keys.
        """
        if self.per_ontology_hyperparams is None:
            return

        for key in self.per_ontology_hyperparams:
            if key not in CAFA_ONTOLOGIES:
                raise ValueError(
                    f"Invalid CAFA ontology: {key}. "
                    f"Expected one of {CAFA_ONTOLOGIES}"
                )

        # Bridge into generic multitask structure
        self.per_task_hyperparams = self.per_ontology_hyperparams


    def get_ontology_params(self, ontology: str) -> Dict[str, Any]:
        """
        Get effective hyperparameters for ontology.
        """
        return self.get_task_params(ontology)