"""Strongly connected components and cycle detection.

This module is intentionally small and dependency-free so it can be reused by
multiple devtools without pulling in heavyweight analyzers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def find_strongly_connected_components(
    graph: Mapping[str, Sequence[str]],
) -> list[list[str]]:
    """Return SCCs of a directed graph using Tarjan's algorithm.

    Args:
        graph: adjacency list (node -> sequence of nodes). Nodes appearing only in
            adjacency lists are treated as nodes with no outgoing edges.

    Returns:
        A list of components, each a sorted list of node IDs. The outer list is
        returned in deterministic order (lexicographic by component then node).
    """
    # Ensure we include nodes that appear only as targets.
    nodes: set[str] = set(graph.keys())
    for deps in graph.values():
        for d in deps:
            nodes.add(d)

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, ()):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)
                if w == v:
                    break
            comp.sort()
            components.append(comp)

    for v in sorted(nodes):
        if v not in indices:
            strongconnect(v)

    components.sort(key=lambda c: (len(c), c))
    return components


def find_cycles(graph: Mapping[str, Sequence[str]]) -> list[list[str]]:
    """Return cycles (SCCs of size>1 plus explicit self-loops).

    Returns:
        Deterministic list of cycles, each a sorted list of node IDs.
    """
    sccs = find_strongly_connected_components(graph)
    cycles: list[list[str]] = [c for c in sccs if len(c) > 1]
    # Self-loops (A -> A) are cycles even though SCC size is 1.
    for node in sorted(graph.keys()):
        deps = graph.get(node, ())
        if node in deps:
            cycles.append([node])
    cycles.sort(key=lambda c: (len(c), c))
    return cycles

