"""Competition infra tier 2: feature-extraction trainer and regression submission."""

from . import feature_extraction

from .feature_extraction import *

__all__ = tuple(list(feature_extraction.__all__))
