"""Graph utilities (infra-level primitive)."""

from .reachability import compute_incoming_counts
from .reachability import induced_subgraph
from .reachability import orphan_cascade_waves
from .reachability import reachable_from_entrypoints
from .import_graph import ImportGraphBuildResult
from .import_graph import TreeEdge
from .import_graph import bounded_bfs_tree_edges
from .import_graph import build_internal_import_graph
from .import_graph import direct_inbound
from .import_graph import direct_outbound
from .import_graph import iter_tree_lines
from .import_graph import resolve_target_module
from .import_graph import transitive_closure
from .scc import find_strongly_connected_components
from .scc import find_cycles

__all__ = [
    "ImportGraphBuildResult",
    "TreeEdge",
    "bounded_bfs_tree_edges",
    "build_internal_import_graph",
    "compute_incoming_counts",
    "direct_inbound",
    "direct_outbound",
    "find_cycles",
    "find_strongly_connected_components",
    "induced_subgraph",
    "iter_tree_lines",
    "orphan_cascade_waves",
    "reachable_from_entrypoints",
    "resolve_target_module",
    "transitive_closure",
]

