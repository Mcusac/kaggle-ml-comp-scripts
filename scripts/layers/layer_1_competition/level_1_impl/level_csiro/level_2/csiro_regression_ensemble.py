"""CSIRO-specific regression ensemble factory.

Wraps the generic RegressionEnsemble with the pickle module alias required
to deserialize models that were originally saved under the 'modeling' namespace.

Contest-specific: not imported by the general ``layer_0_core`` stack.
"""

from typing import Any, Dict, List, Optional

from layers.layer_0_core.level_8 import RegressionEnsemble, create_regression_ensemble_from_paths

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import csiro_modeling

_CSIRO_PICKLE_ALIASES: Dict[str, Any] = {
    "modeling": csiro_modeling,
}


def create_csiro_regression_ensemble(
    model_paths: List[str],
    model_configs: List[Dict[str, Any]],
    method: str = "weighted_average",
    feature_extraction_model_name: Optional[str] = None,
    cv_scores: Optional[List[float]] = None,
) -> RegressionEnsemble:
    """
    Create a RegressionEnsemble pre-configured with the CSIRO pickle alias.

    Identical to create_regression_ensemble_from_paths but always injects
    the 'modeling' -> csiro_modeling alias needed to unpickle CSIRO models.

    Args:
        model_paths: Paths to model directories or .pkl files.
        model_configs: Per-model config dicts (must match model_paths length).
        method: Ensembling method name.
        feature_extraction_model_name: Override for the feature extractor name.
        cv_scores: Per-model CV scores for weighted/ranked/percentile methods.

    Returns:
        Configured and loaded RegressionEnsemble.
    """
    return create_regression_ensemble_from_paths(
        model_paths=model_paths,
        model_configs=model_configs,
        method=method,
        feature_extraction_model_name=feature_extraction_model_name,
        cv_scores=cv_scores,
        pickle_module_aliases=_CSIRO_PICKLE_ALIASES,
    )
