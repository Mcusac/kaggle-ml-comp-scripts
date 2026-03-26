"""Factory for creating ensembling methods by name."""

from layers.layer_0_core.level_0 import EnsemblingMethod
from level_3 import PerTargetWeightedEnsemble
from level_6 import (
    SimpleAverageEnsemble,
    WeightedAverageEnsemble,
    RankedAverageEnsemble,
    PercentileAverageEnsemble,
    TargetSpecificEnsemble,
)


def create_ensembling_method(method_name: str, **kwargs) -> EnsemblingMethod:
    """
    Create ensembling method by name.

    Args:
        method_name: One of 'simple_average', 'weighted_average', 'ranked_average',
            'percentile_average', 'target_specific', 'per_target_weighted'.
        **kwargs: Passed to target_specific and per_target_weighted constructors.

    Returns:
        EnsemblingMethod instance.
    """
    if method_name == 'simple_average':
        return SimpleAverageEnsemble()
    if method_name == 'weighted_average':
        return WeightedAverageEnsemble()
    if method_name == 'ranked_average':
        return RankedAverageEnsemble()
    if method_name == 'percentile_average':
        return PercentileAverageEnsemble()
    if method_name == 'target_specific':
        return TargetSpecificEnsemble(**kwargs)
    if method_name == 'per_target_weighted':
        return PerTargetWeightedEnsemble(**kwargs)
    raise ValueError(
        f"Unknown ensembling method: {method_name}. "
        "Valid: 'simple_average', 'weighted_average', 'ranked_average', "
        "'percentile_average', 'target_specific', 'per_target_weighted'"
    )
