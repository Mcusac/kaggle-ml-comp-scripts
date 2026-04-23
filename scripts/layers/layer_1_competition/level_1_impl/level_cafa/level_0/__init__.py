"""Auto-generated package exports."""


from .config import CAFAConfig

from .constants import (
    CAFA_ONTOLOGIES,
    validate_ontology,
)

from .data_schema import CAFADataSchema

from .embedding_paths import (
    EMBEDDING_TYPE_ALIASES,
    get_embedding_paths,
    normalize_embedding_type_cafa,
    resolve_base_path,
    resolve_embedding_paths,
)

from .goa_filter import GOAFilter

from .hierarchy import CAFAHierarchy

from .ontology import CAFAOntologySystem

from .ontology_data_loader import OntologyDataLoader

from .ontology_model_manager import OntologyModelManager

from .paths import CAFAPaths

from .t5_loader import (
    load_t5_qs,
    load_t5_rds,
)

from .threshold_optimization import (
    load_ia_weights,
    optimize_threshold_ia_weighted,
)

__all__ = [
    "CAFAConfig",
    "CAFADataSchema",
    "CAFAHierarchy",
    "CAFAOntologySystem",
    "CAFAPaths",
    "CAFA_ONTOLOGIES",
    "EMBEDDING_TYPE_ALIASES",
    "GOAFilter",
    "OntologyDataLoader",
    "OntologyModelManager",
    "get_embedding_paths",
    "load_ia_weights",
    "load_t5_qs",
    "load_t5_rds",
    "normalize_embedding_type_cafa",
    "optimize_threshold_ia_weighted",
    "resolve_base_path",
    "resolve_embedding_paths",
    "validate_ontology",
]
