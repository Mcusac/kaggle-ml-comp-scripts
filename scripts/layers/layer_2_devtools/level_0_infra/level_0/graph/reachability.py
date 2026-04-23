"""Reachability and dead-candidate utilities for module dependency graphs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def reachable_from_entrypoints(
    *, graph: Mapping[str, Sequence[str]], entrypoints: set[str]
) -> set[str]:
    """Return nodes reachable from entrypoints (inclusive).

    Args:
        graph: adjacency list (node -> sequence of nodes).
        entrypoints: starting nodes.
    """
    seen: set[str] = set()
    stack = list(sorted(entrypoints))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for nxt in sorted(graph.get(cur, ())):
            if nxt not in seen:
                stack.append(nxt)
    return seen


def induced_subgraph(
    *, graph: Mapping[str, Sequence[str]], nodes: set[str]
) -> dict[str, list[str]]:
    """Return a graph restricted to `nodes` (edges to outside nodes are dropped)."""
    out: dict[str, list[str]] = {}
    for n in sorted(nodes):
        deps = [d for d in graph.get(n, ()) if d in nodes]
        out[n] = sorted(set(deps))
    return out


def compute_incoming_counts(
    *, graph: Mapping[str, Sequence[str]], nodes: set[str]
) -> dict[str, int]:
    """Compute incoming edge counts within `nodes`."""
    counts: dict[str, int] = {n: 0 for n in nodes}
    for src in nodes:
        for dst in graph.get(src, ()):
            if dst in counts:
                counts[dst] += 1
    return counts


def orphan_cascade_waves(
    *,
    graph: Mapping[str, Sequence[str]],
    nodes: set[str],
    excluded: set[str] | None = None,
) -> list[list[str]]:
    """Iteratively peel orphans (no incoming edges) until fixed point.

    Notes:
    - `excluded` nodes are never selected as cascade candidates, but they still
      participate in incoming-edge computations (i.e., they can keep a node from
      becoming an orphan).
    """
    excluded = excluded or set()

    remaining: set[str] = set(nodes)
    waves: list[list[str]] = []

    while True:
        incoming = compute_incoming_counts(graph=graph, nodes=remaining)
        wave = sorted(
            [
                n
                for n, cnt in incoming.items()
                if cnt == 0 and n not in excluded
            ]
        )
        if not wave:
            break
        waves.append(wave)
        for n in wave:
            remaining.discard(n)

    return waves

