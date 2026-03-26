"""Extension point infrastructure: framework Protocols and the model factory registry."""

from .ensembling_method import EnsemblingMethod
from .grid_search_context import GridSearchContext
from .handler_context_builder import HandlerContextBuilder
from .metric import Metric
from .model_registry import ModelRegistry

__all__ = [
    "EnsemblingMethod",
    "GridSearchContext",
    "HandlerContextBuilder",
    "Metric",
    "ModelRegistry",
]
