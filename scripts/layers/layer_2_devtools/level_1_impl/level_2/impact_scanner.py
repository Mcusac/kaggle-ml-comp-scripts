#!/usr/bin/env python3
"""
Impact scanner (who imports this file? what does it import?).

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python layers/layer_2_devtools/level_1_impl/level_2/impact_scanner.py --help

Writes ``impact_scan_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``impact_scan.v1`` when ``--json`` is provided).
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Any

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]


def _load_module_from_path(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _ensure_pkg(mod_name: str, pkg_path: Path) -> None:
    if mod_name in sys.modules:
        return
    m = ModuleType(mod_name)
    m.__path__ = [str(pkg_path)]
    sys.modules[mod_name] = m


# Avoid importing package `__init__.py` aggregators (they can pull optional deps).
_ensure_pkg("layers", _SCRIPTS / "layers")
_ensure_pkg("layers.layer_2_devtools", _SCRIPTS / "layers" / "layer_2_devtools")
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.graph",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0" / "graph",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.path",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0" / "path",
)

_IMPORT_GRAPH = _load_module_from_path(
    "_impact_scanner_import_graph",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "graph"
    / "import_graph.py",
)
_PYMODS = _load_module_from_path(
    "_impact_scanner_pymods",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "python_modules.py",
)
_WORKSPACE = _load_module_from_path(
    "_impact_scanner_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)

build_internal_import_graph = _IMPORT_GRAPH.build_internal_import_graph
bounded_bfs_tree_edges = _IMPORT_GRAPH.bounded_bfs_tree_edges
direct_inbound = _IMPORT_GRAPH.direct_inbound
direct_outbound = _IMPORT_GRAPH.direct_outbound
iter_tree_lines = _IMPORT_GRAPH.iter_tree_lines
resolve_target_module = _IMPORT_GRAPH.resolve_target_module
ImportGraphBuildResult = _IMPORT_GRAPH.ImportGraphBuildResult

file_to_module = _PYMODS.file_to_module
resolve_workspace_root = _WORKSPACE.resolve_workspace_root


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _normalize_target_path(*, target: Path, root: Path) -> Path | None:
    p = target
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    try:
        p_rel = p.relative_to(root.resolve())
        return (root / p_rel).resolve()
    except ValueError:
        # allow absolute paths anywhere, but they must still be within root
        return None


def _compute_payload(
    *,
    target_file: Path,
    root: Path,
    include_tests: bool,
    max_depth: int,
    max_nodes: int,
    generated: date,
    workspace: Path,
) -> dict[str, Any]:
    build: ImportGraphBuildResult = build_internal_import_graph(root=root, include_tests=include_tests)
    module = resolve_target_module(target_file=target_file, root=root)
    if not module:
        return {
            "schema": "impact_scan.v1",
            "generated": generated.isoformat(),
            "workspace": workspace.as_posix(),
            "root": root.resolve().as_posix(),
            "target_file": target_file.resolve().as_posix(),
            "target_module": None,
            "include_tests": bool(include_tests),
            "files_scanned": int(build.files_scanned),
            "parse_error_count": int(build.parse_error_count),
            "error": "Could not resolve target_file to a module under root.",
        }

    out_direct = direct_outbound(graph=build.graph, module=module)
    in_direct = direct_inbound(reverse_graph=build.reverse_graph, module=module)

    forward_edges = bounded_bfs_tree_edges(
        graph=build.graph, start=module, max_depth=max_depth, max_nodes=max_nodes
    )
    reverse_edges = bounded_bfs_tree_edges(
        graph=build.reverse_graph, start=module, max_depth=max_depth, max_nodes=max_nodes
    )
    forward_lines = iter_tree_lines(root=module, edges=forward_edges, max_lines=max(50, max_nodes))
    reverse_lines = iter_tree_lines(root=module, edges=reverse_edges, max_lines=max(50, max_nodes))

    return {
        "schema": "impact_scan.v1",
        "generated": generated.isoformat(),
        "workspace": workspace.as_posix(),
        "root": root.resolve().as_posix(),
        "target_file": target_file.resolve().as_posix(),
        "target_module": module,
        "include_tests": bool(include_tests),
        "files_scanned": int(build.files_scanned),
        "parse_error_count": int(build.parse_error_count),
        "outbound_direct": out_direct,
        "inbound_direct": in_direct,
        "forward_tree_lines": forward_lines,
        "reverse_tree_lines": reverse_lines,
        "max_depth": int(max_depth),
        "max_nodes": int(max_nodes),
    }


def _write_artifacts(
    *, output_dir: Path, payload: dict[str, Any], write_json: bool
) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = str(payload["generated"])
    md_path = output_dir / f"impact_scan_{generated}.md"

    lines: list[str] = [
        "---",
        f"generated: {payload['generated']}",
        "artifact: impact_scan",
        f"schema: {payload['schema']}",
        f"root: {payload['root']}",
        "---",
        "",
        "# Impact scan",
        "",
        f"- Root: `{payload['root']}`",
        f"- Target file: `{payload['target_file']}`",
        f"- Target module: `{payload.get('target_module')}`",
        f"- Files scanned: {int(payload.get('files_scanned', 0))}",
        f"- Parse errors: {int(payload.get('parse_error_count', 0))}",
        f"- include_tests: {bool(payload.get('include_tests', False))}",
        "",
    ]

    err = payload.get("error")
    if err:
        lines.append(f"❌ {err}")
        lines.append("")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        out: dict[str, str | int] = {"md_path": str(md_path), "exit_code_hint": 2}
        if write_json:
            json_path = output_dir / f"impact_scan_{generated}.json"
            json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            out["json_path"] = str(json_path)
        return out

    lines.append("## Direct outbound (imports)")
    lines.append("")
    outbound = list(payload.get("outbound_direct", []))
    if not outbound:
        lines.append("✅ None.")
    else:
        for m in outbound:
            lines.append(f"- `{m}`")
    lines.append("")

    lines.append("## Direct inbound (importers)")
    lines.append("")
    inbound = list(payload.get("inbound_direct", []))
    if not inbound:
        lines.append("✅ None.")
    else:
        for m in inbound:
            lines.append(f"- `{m}`")
    lines.append("")

    lines.append("## Forward tree (transitive outbound)")
    lines.append("")
    for s in payload.get("forward_tree_lines", []):
        lines.append(f"- `{s}`" if s == payload.get("target_module") else f"  {s}")
    lines.append("")

    lines.append("## Reverse tree (transitive inbound)")
    lines.append("")
    for s in payload.get("reverse_tree_lines", []):
        lines.append(f"- `{s}`" if s == payload.get("target_module") else f"  {s}")
    lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out2: dict[str, str | int] = {"md_path": str(md_path)}
    if write_json:
        json_path = output_dir / f"impact_scan_{generated}.json"
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out2["json_path"] = str(json_path)
    return out2


def main() -> int:
    _win_utf8_stdio()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target_file",
        type=Path,
        help="Target Python file to analyze (path under --root).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=_SCRIPTS,
        help="Root directory to scan for Python modules (default: scripts/).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write reports here (default: <workspace>/.cursor/audit-results/general/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filenames (default: today).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write impact_scan_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="Max traversal depth for forward/reverse trees.",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=2000,
        help="Max discovered nodes in tree traversals (safety cap).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"❌ Root is not a directory: {root}", file=sys.stderr)
        return 2

    normalized = _normalize_target_path(target=args.target_file, root=root)
    if normalized is None or not normalized.is_file():
        print(
            f"❌ target_file must be a file under --root. target_file={args.target_file} root={root}",
            file=sys.stderr,
        )
        return 2

    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    payload = _compute_payload(
        target_file=normalized,
        root=root,
        include_tests=bool(args.include_tests),
        max_depth=int(args.max_depth),
        max_nodes=int(args.max_nodes),
        generated=generated,
        workspace=workspace,
    )
    paths = _write_artifacts(output_dir=output_dir, payload=payload, write_json=bool(args.json))

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(
        "[SUMMARY] "
        f"target_module={payload.get('target_module')} "
        f"inbound={len(payload.get('inbound_direct', []))} "
        f"outbound={len(payload.get('outbound_direct', []))} "
        f"parse_errors={int(payload.get('parse_error_count', 0))}"
    )

    return 0 if not payload.get("error") else 2


if __name__ == "__main__":
    raise SystemExit(main())

