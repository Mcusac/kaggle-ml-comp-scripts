"""Boundary validation primitives (nodes, classification, spec)."""

from .boundary_classifiers import BoundaryClassifyResult, classify_module_to_boundary
from .boundary_nodes import BoundaryNode
from .boundary_spec import BoundaryDecision, PackageBoundarySpec

__all__ = [
    "BoundaryClassifyResult",
    "BoundaryDecision",
    "BoundaryNode",
    "PackageBoundarySpec",
    "classify_module_to_boundary",
]

