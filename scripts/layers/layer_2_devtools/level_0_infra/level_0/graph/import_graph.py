"""Internal import-graph builder and traversal helpers.

This module is intentionally small and dependency-light so multiple devtools can
reuse a consistent view of the internal import graph.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    get_imports_from_ast,
    parse_file,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    discover_packages,
    file_to_module,
    is_internal_module,
)


@dataclass(frozen=True)
class ImportGraphBuildResult:
    graph: dict[str, list[str]]
    reverse_graph: dict[str, list[str]]
    parse_error_count: int
    files_scanned: int


def build_internal_import_graph(
    *, root: Path, include_tests: bool = False
) -> ImportGraphBuildResult:
    """Build an internal-only import graph for Python modules under `root`.

    Notes:
    - Only modules whose top-level package exists under `root` are included as nodes.
    - Edges point from importer -> imported module (direct imports only).
    - A reverse adjacency (imported -> importers) is returned for inbound queries.
    """
    files = collect_python_files(root, include_tests=include_tests)
    internal_packages = discover_packages(root)

    parse_error_count = 0
    graph: dict[str, list[str]] = {}
    reverse: dict[str, set[str]] = {}

    for file_path in files:
        module = file_to_module(file_path, root)
        if not module:
            continue

        tree = parse_file(file_path)
        if tree is None:
            parse_error_count += 1
            graph.setdefault(module, [])
            continue

        pkg = current_package(file_path, root)
        imports = get_imports_from_ast(tree, pkg)
        internal = sorted([m for m in imports.keys() if is_internal_module(m, internal_packages)])
        graph[module] = internal

        for dep in internal:
            reverse.setdefault(dep, set()).add(module)

    reverse_graph: dict[str, list[str]] = {k: sorted(v) for k, v in reverse.items()}
    return ImportGraphBuildResult(
        graph=graph,
        reverse_graph=reverse_graph,
        parse_error_count=parse_error_count,
        files_scanned=len(files),
    )


def resolve_target_module(*, target_file: Path, root: Path) -> str | None:
    """Resolve a target file path to a module name relative to `root`."""
    return file_to_module(target_file, root)


def direct_outbound(*, graph: Mapping[str, Sequence[str]], module: str) -> list[str]:
    return sorted(set(graph.get(module, ())))


def direct_inbound(*, reverse_graph: Mapping[str, Sequence[str]], module: str) -> list[str]:
    return sorted(set(reverse_graph.get(module, ())))


def transitive_closure(
    *,
    graph: Mapping[str, Sequence[str]],
    start: str,
    max_depth: int = 25,
    max_nodes: int = 10_000,
) -> set[str]:
    """Return all nodes reachable from `start` (excluding `start`)."""
    if max_depth < 0 or max_nodes < 0:
        return set()

    seen: set[str] = {start}
    out: set[str] = set()
    q: deque[tuple[str, int]] = deque([(start, 0)])
    while q and len(seen) <= max_nodes:
        node, depth = q.popleft()
        if depth >= max_depth:
            continue
        for nxt in graph.get(node, ()):
            if nxt in seen:
                continue
            seen.add(nxt)
            out.add(nxt)
            q.append((nxt, depth + 1))
            if len(seen) > max_nodes:
                break
    return out


@dataclass(frozen=True)
class TreeEdge:
    parent: str
    child: str
    depth: int


def bounded_bfs_tree_edges(
    *,
    graph: Mapping[str, Sequence[str]],
    start: str,
    max_depth: int = 10,
    max_nodes: int = 2_000,
) -> list[TreeEdge]:
    """Return BFS tree edges rooted at `start` with depth/node caps.

    The returned edges represent one chosen parent for each discovered node.
    """
    if max_depth < 0 or max_nodes < 0:
        return []

    seen: set[str] = {start}
    edges: list[TreeEdge] = []
    q: deque[tuple[str, int]] = deque([(start, 0)])

    while q and len(seen) <= max_nodes:
        node, depth = q.popleft()
        if depth >= max_depth:
            continue
        for nxt in sorted(set(graph.get(node, ()))):
            if nxt in seen:
                continue
            seen.add(nxt)
            edges.append(TreeEdge(parent=node, child=nxt, depth=depth + 1))
            q.append((nxt, depth + 1))
            if len(seen) > max_nodes:
                break

    return edges


def iter_tree_lines(
    *,
    root: str,
    edges: Sequence[TreeEdge],
    max_lines: int = 2_000,
) -> list[str]:
    """Render tree edges as indented lines; deterministic by child name."""
    by_parent: dict[str, list[TreeEdge]] = {}
    for e in edges:
        by_parent.setdefault(e.parent, []).append(e)
    for parent, xs in by_parent.items():
        by_parent[parent] = sorted(xs, key=lambda x: x.child)

    lines: list[str] = [root]

    def walk(node: str, *, indent: str) -> None:
        if len(lines) >= max_lines:
            return
        for e in by_parent.get(node, ()):
            if len(lines) >= max_lines:
                return
            lines.append(f"{indent}- {e.child}")
            walk(e.child, indent=indent + "  ")

    walk(root, indent="")
    return lines[: max(1, int(max_lines))]

