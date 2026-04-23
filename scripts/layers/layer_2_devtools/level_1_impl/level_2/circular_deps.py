#!/usr/bin/env python3
"""
Circular dependency detector for Python modules under a chosen root.

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python layers/layer_2_devtools/level_1_impl/level_2/circular_deps.py --help

Writes ``circular_deps_scan_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``circular_deps_scan.v1`` when ``--json`` is provided).
"""

from __future__ import annotations

import argparse
import json
import importlib.util
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import ModuleType

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]


def _load_module_from_path(name: str, path: Path):
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
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.parse",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0" / "parse",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.parse.ast",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "parse"
    / "ast",
)

_SCC = _load_module_from_path(
    "_circular_deps_scc",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "graph"
    / "scc.py",
)
_IMPORT_GRAPH = _load_module_from_path(
    "_circular_deps_import_graph",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "graph"
    / "import_graph.py",
)
_WORKSPACE = _load_module_from_path(
    "_circular_deps_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)

find_cycles = _SCC.find_cycles
resolve_workspace_root = _WORKSPACE.resolve_workspace_root
build_internal_import_graph = _IMPORT_GRAPH.build_internal_import_graph


@dataclass(frozen=True)
class CycleFinding:
    nodes: list[str]
    chain: list[str]


def _build_internal_import_graph(
    *, root: Path, include_tests: bool = False
) -> tuple[dict[str, list[str]], int]:
    res = build_internal_import_graph(root=root, include_tests=include_tests)
    return dict(res.graph), int(res.parse_error_count)


def _cycle_chain_for_component(
    *, component: list[str], graph: dict[str, list[str]]
) -> list[str]:
    nodes = sorted(component)
    allowed = set(nodes)
    subgraph = {n: sorted([d for d in graph.get(n, []) if d in allowed]) for n in nodes}

    if len(nodes) == 1:
        n = nodes[0]
        if n in subgraph.get(n, []):
            return [n, n]
        return [n]

    for start in nodes:
        stack: list[str] = []
        in_stack: set[str] = set()

        def dfs(v: str) -> list[str] | None:
            stack.append(v)
            in_stack.add(v)
            for w in subgraph.get(v, []):
                if w == start and len(stack) >= 2:
                    return [*stack, start]
                if w not in in_stack:
                    found = dfs(w)
                    if found is not None:
                        return found
            in_stack.remove(v)
            stack.pop()
            return None

        found = dfs(start)
        if found is not None:
            return found

    # SCC implies a cycle exists; if we fail to reconstruct deterministically, fall back.
    return [nodes[0], nodes[0]]


def _write_artifacts(
    *,
    workspace: Path,
    output_dir: Path,
    generated: date,
    root: Path,
    parse_error_count: int,
    cycles: list[CycleFinding],
    write_json: bool,
) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"circular_deps_scan_{generated.isoformat()}.md"

    lines: list[str] = [
        "---",
        f"generated: {generated.isoformat()}",
        "artifact: circular_deps_scan",
        "schema: circular_deps_scan.v1",
        f"root: {root.resolve().as_posix()}",
        "---",
        "",
        "# Circular dependency scan",
        "",
        f"- Root: `{root.resolve().as_posix()}`",
        f"- Files with parse errors: {parse_error_count}",
        f"- Cycle components: {len(cycles)}",
        "",
    ]
    if not cycles:
        lines.append("✅ No circular dependencies detected.")
        lines.append("")
    else:
        lines.append("## Cycles")
        lines.append("")
        for idx, c in enumerate(cycles, start=1):
            chain = " -> ".join(c.chain)
            lines.append(f"{idx}. **{len(c.nodes)} modules**")
            lines.append(f"   - Chain: `{chain}`")
            lines.append(f"   - Nodes: `{', '.join(c.nodes)}`")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {"md_path": str(md_path), "cycle_count": len(cycles)}
    if write_json:
        payload = {
            "schema": "circular_deps_scan.v1",
            "generated": generated.isoformat(),
            "workspace": workspace.as_posix(),
            "root": root.resolve().as_posix(),
            "parse_error_count": parse_error_count,
            "cycle_count": len(cycles),
            "cycles": [{"nodes": c.nodes, "chain": c.chain} for c in cycles],
        }
        json_path = output_dir / f"circular_deps_scan_{generated.isoformat()}.json"
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out["json_path"] = str(json_path)
    return out


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
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
        help="Also write circular_deps_scan_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded).",
    )
    parser.add_argument(
        "--fail-on-cycles",
        action="store_true",
        help="Exit with code 1 if cycle_count exceeds --max-cycles (default 0).",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=0,
        help="When using --fail-on-cycles, allow up to this many cycles (default: 0).",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit 1 if any file failed to parse.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    graph, parse_error_count = _build_internal_import_graph(
        root=root, include_tests=bool(args.include_tests)
    )
    components = find_cycles(graph)
    findings = [
        CycleFinding(nodes=sorted(comp), chain=_cycle_chain_for_component(component=comp, graph=graph))
        for comp in components
    ]
    findings.sort(key=lambda c: (len(c.nodes), c.nodes))

    paths = _write_artifacts(
        workspace=workspace,
        output_dir=output_dir,
        generated=generated,
        root=root,
        parse_error_count=parse_error_count,
        cycles=findings,
        write_json=bool(args.json),
    )

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(f"[SUMMARY] parse_errors={parse_error_count} cycles={paths['cycle_count']}")

    exit_code = 0
    if args.fail_on_cycles:
        max_c = max(0, int(args.max_cycles))
        ccount = int(paths.get("cycle_count", 0))
        if ccount > max_c:
            print(
                f"❌ [FAIL] cycle_count={ccount} exceeds --max-cycles={max_c}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_parse_errors and parse_error_count > 0:
        print(f"❌ [FAIL] parse_error_count={parse_error_count}", file=sys.stderr)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

