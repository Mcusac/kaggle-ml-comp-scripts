"""Prediction combination helpers and ensemble strategies."""

from .combine import apply_weighted_combination, combine_with_fallback
from .stacking_ensemble import StackingEnsemble

__all__ = [
    "apply_weighted_combination",
    "combine_with_fallback",
    "StackingEnsemble",
]