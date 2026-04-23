from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.graph.import_graph import (
    bounded_bfs_tree_edges,
    build_internal_import_graph,
    direct_inbound,
    direct_outbound,
    iter_tree_lines,
    resolve_target_module,
)


def _write(pkg_root: Path, rel: str, text: str) -> Path:
    p = pkg_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_build_internal_import_graph_forward_and_reverse(tmp_path: Path) -> None:
    # Root packages: a, b
    _write(tmp_path, "a/__init__.py", "__all__ = ()\n")
    _write(tmp_path, "b/__init__.py", "__all__ = ()\n")
    a_mod = _write(tmp_path, "a/mod.py", "from b import util\n")
    _write(tmp_path, "b/util.py", "x = 1\n")

    res = build_internal_import_graph(root=tmp_path, include_tests=False)
    assert res.parse_error_count == 0

    assert res.graph["a.mod"] == ["b.util"]
    assert res.graph["b.util"] == []

    assert res.reverse_graph["b.util"] == ["a.mod"]
    assert direct_outbound(graph=res.graph, module="a.mod") == ["b.util"]
    assert direct_inbound(reverse_graph=res.reverse_graph, module="b.util") == ["a.mod"]

    assert resolve_target_module(target_file=a_mod, root=tmp_path) == "a.mod"


def test_build_internal_import_graph_counts_parse_errors(tmp_path: Path) -> None:
    _write(tmp_path, "a/__init__.py", "__all__ = ()\n")
    _write(tmp_path, "a/bad.py", "def oops(:\n")

    res = build_internal_import_graph(root=tmp_path, include_tests=False)
    assert res.parse_error_count == 1
    assert "a.bad" in res.graph
    assert res.graph["a.bad"] == []


def test_bounded_tree_edges_and_rendering_limits() -> None:
    g = {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}

    edges_depth1 = bounded_bfs_tree_edges(graph=g, start="a", max_depth=1, max_nodes=100)
    assert [e.child for e in edges_depth1] == ["b"]

    edges_depth2 = bounded_bfs_tree_edges(graph=g, start="a", max_depth=2, max_nodes=100)
    assert [e.child for e in edges_depth2] == ["b", "c"]

    lines = iter_tree_lines(root="a", edges=edges_depth2, max_lines=10)
    assert lines[0] == "a"
    assert "- b" in lines[1]

