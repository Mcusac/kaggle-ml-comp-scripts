"""Extension point infrastructure: framework Protocols and the model factory registry."""

from .ensembling_method import EnsemblingMethod
from .grid_search_context import GridSearchContext
from .handler_context_builder import HandlerContextBuilder
from .metric import Metric
from .model_registry import ModelRegistry
from .named_registry import NamedRegistry, build_unknown_key_error
from .pipeline_result import PipelineResult

__all__ = [
    "EnsemblingMethod",
    "GridSearchContext",
    "HandlerContextBuilder",
    "Metric",
    "ModelRegistry",
    "NamedRegistry",
    "build_unknown_key_error",
    "PipelineResult",
]
