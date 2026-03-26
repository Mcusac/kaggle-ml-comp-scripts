"""CAFA-specific parameter grid resolution and grid search extensions.

Per-ontology parameter grid support for CAFA 6, where different ontologies
(F, P, C) may have different optimal hyperparameters.
"""

from typing import Any, Dict, List, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import resolve_keyed_param_grid

from layers.layer_1_competition.level_1_impl.level_cafa.level_0 import validate_ontology

logger = get_logger(__name__)


def resolve_cafa_param_grid(
    grid_config: Dict[str, Any],
    ontology: Optional[str] = None,
    quick_mode: bool = False,
) -> Dict[str, List]:
    """
    Resolve parameter grid for CAFA ontology.
    """
    if ontology:
        validate_ontology(ontology)
    return resolve_keyed_param_grid(
        grid_config=grid_config,
        key=ontology,
        quick_mode=quick_mode,
        keyed_grids_field="param_grids",
    )


def get_ontology_param_grid(ontology: str, config: Any) -> Dict[str, List]:
    """
    Get parameter grid for specific ontology if per-ontology grids are available.

    Returns per-ontology parameter grid if available in config, otherwise falls back
    to default grid. Allows targeted optimization per ontology (F, P, C).

    Args:
        ontology: Ontology identifier ('F', 'P', or 'C').
        config: Configuration object with per-ontology grid definitions.
            Should have 'param_grids' dict with ontology keys, or 'param_grid' for default.

    Returns:
        Parameter grid dict (per-ontology if available, else default grid).
    """
    validate_ontology(ontology)

    if hasattr(config, "param_grids"):
        param_grids = config.param_grids
        if isinstance(param_grids, dict) and ontology in param_grids:
            logger.info("Using per-ontology grid for %s ontology", ontology)
            return param_grids[ontology]

    if isinstance(config, dict):
        if "param_grids" in config and isinstance(config["param_grids"], dict):
            if ontology in config["param_grids"]:
                logger.info("Using per-ontology grid for %s ontology", ontology)
                return config["param_grids"][ontology]

    logger.info("Using default parameter grid for %s ontology", ontology)
    return get_default_param_grid(config)


def get_default_param_grid(config: Any) -> Dict[str, List]:
    """
    Get default parameter grid (unified across all ontologies).

    Returns the default/unified parameter grid from config. Used when
    per-ontology grids are not available or when a unified grid is preferred.

    Args:
        config: Configuration object with 'param_grid' attribute or dict key.

    Returns:
        Default parameter grid dict.
    """
    if hasattr(config, "param_grid"):
        return config.param_grid

    if isinstance(config, dict) and "param_grid" in config:
        return config["param_grid"]

    logger.warning("No parameter grid found in config, using minimal default grid")
    return {
        "learning_rate": [1e-3],
        "batch_size": [32],
    }
