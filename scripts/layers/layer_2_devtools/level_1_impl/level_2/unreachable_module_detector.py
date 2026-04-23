#!/usr/bin/env python3
"""
Unreachable module detector (cascade + reachability).

Reports:
- Unreachable-from-entrypoints modules (reachability in the import graph)
- Cascade dead detection waves (iterative orphan peeling)
- SCC grouping of unreachable clusters (cleanup ordering)

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.unreachable_module_detector --help

Writes ``unreachable_module_detector_run_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``unreachable_module_detector_run.v1`` when ``--json`` is provided).
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
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.models",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0" / "models",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_1",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_1",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_1.health_analyzers",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_1"
    / "health_analyzers",
)

_REACHABILITY = _load_module_from_path(
    "_unreachable_module_detector_reachability",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "graph"
    / "reachability.py",
)
_SCC = _load_module_from_path(
    "_unreachable_module_detector_scc",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "graph"
    / "scc.py",
)
_DEAD_FILE_CONFIG = _load_module_from_path(
    "_unreachable_module_detector_dead_file_config",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "models"
    / "dead_file_config.py",
)
_PYMODS = _load_module_from_path(
    "_unreachable_module_detector_pymods",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "python_modules.py",
)
_WORKSPACE = _load_module_from_path(
    "_unreachable_module_detector_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)
_IMPORT_ANALYZER = _load_module_from_path(
    "_unreachable_module_detector_import_analyzer",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_1"
    / "health_analyzers"
    / "import_analyzer.py",
)

DeadFileConfig = _DEAD_FILE_CONFIG.DeadFileConfig
discover_packages = _PYMODS.discover_packages
is_internal_module = _PYMODS.is_internal_module
module_to_file_path = _PYMODS.module_to_file_path
resolve_workspace_root = _WORKSPACE.resolve_workspace_root
ImportAnalyzer = _IMPORT_ANALYZER.ImportAnalyzer

reachable_from_entrypoints = _REACHABILITY.reachable_from_entrypoints
induced_subgraph = _REACHABILITY.induced_subgraph
orphan_cascade_waves = _REACHABILITY.orphan_cascade_waves
find_strongly_connected_components = _SCC.find_strongly_connected_components


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _compute_clusters(graph: dict[str, list[str]], members: set[str]) -> list[list[str]]:
    if not members:
        return []
    sub = induced_subgraph(graph=graph, nodes=members)
    comps = find_strongly_connected_components(sub)
    clusters = [c for c in comps if len(c) > 1]
    clusters.sort(key=lambda c: (-len(c), c))
    return clusters


def _compute_run_payload(
    *,
    root: Path,
    config: DeadFileConfig,
    include_tests: bool,
    generated: date,
    workspace: Path,
) -> dict[str, Any]:
    imports = ImportAnalyzer(root).analyze()
    import_map = imports.get("import_map", {}) or {}

    internal_packages = discover_packages(root)
    all_modules = sorted([m for m in import_map.keys() if is_internal_module(m, internal_packages)])

    entrypoints = set(config.entrypoint_modules)
    missing_entrypoints = sorted([m for m in entrypoints if m not in set(all_modules)])

    allow_modules = set(config.allow_modules)
    allow_prefixes = tuple(config.allow_module_prefixes)

    def allowed(m: str) -> bool:
        if not m:
            return True
        if m in allow_modules:
            return True
        return any(m.startswith(pfx) for pfx in allow_prefixes)

    # Unreachable-from-entrypoints (base reachability)
    unreachable: list[str] = []
    if entrypoints:
        reachable = reachable_from_entrypoints(graph=import_map, entrypoints=entrypoints)
        unreachable = sorted([m for m in all_modules if m not in reachable and not allowed(m)])

    # Cascade waves (iterative orphan peeling)
    # Candidates exclude entrypoints and allowed modules/prefixes, but they still
    # participate in the graph so incoming edges remain meaningful.
    excluded_from_cascade = set(entrypoints)
    excluded_from_cascade |= {m for m in all_modules if allowed(m)}
    # Package namespace modules (`a.b` for `a/b/__init__.py`) are not meaningful
    # removal candidates; keep them out of cascade candidates.
    for m in all_modules:
        p = module_to_file_path(root=root, module=m)
        if p is not None and p.name == "__init__.py":
            excluded_from_cascade.add(m)
    cascade_waves = orphan_cascade_waves(
        graph=import_map,
        nodes=set(all_modules),
        excluded=excluded_from_cascade,
    )
    cascade_candidates = sorted({m for wave in cascade_waves for m in wave})

    # SCC clusters for unreachable and cascade candidates (cleanup ordering)
    unreachable_clusters = _compute_clusters(import_map, set(unreachable))
    cascade_clusters = _compute_clusters(import_map, set(cascade_candidates))

    return {
        "schema": "unreachable_module_detector_run.v1",
        "generated": generated.isoformat(),
        "workspace": workspace.as_posix(),
        "root": root.resolve().as_posix(),
        "include_tests": bool(include_tests),
        "entrypoint_modules": sorted(entrypoints),
        "missing_entrypoint_modules": missing_entrypoints,
        "allow_modules": sorted(allow_modules),
        "allow_module_prefixes": list(allow_prefixes),
        "module_count": int(len(all_modules)),
        "unreachable_count": int(len(unreachable)),
        "unreachable_modules": list(unreachable),
        "cascade_wave_count": int(len(cascade_waves)),
        "cascade_candidate_count": int(len(cascade_candidates)),
        "cascade_waves": [list(w) for w in cascade_waves],
        "cascade_candidates": cascade_candidates,
        "unreachable_scc_clusters": unreachable_clusters,
        "cascade_scc_clusters": cascade_clusters,
    }


def _write_artifacts(*, output_dir: Path, payload: dict[str, Any], write_json: bool) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = str(payload["generated"])
    md_path = output_dir / f"unreachable_module_detector_run_{generated}.md"

    unreachable = list(payload.get("unreachable_modules", []))
    waves = list(payload.get("cascade_waves", []))
    un_clusters = list(payload.get("unreachable_scc_clusters", []))
    cs_clusters = list(payload.get("cascade_scc_clusters", []))

    lines: list[str] = [
        "---",
        f"generated: {payload['generated']}",
        "artifact: unreachable_module_detector_run",
        f"schema: {payload['schema']}",
        f"root: {payload['root']}",
        "---",
        "",
        "# Unreachable module detector",
        "",
        f"- Root: `{payload['root']}`",
        f"- Modules (internal): {int(payload.get('module_count', 0))}",
        f"- Entrypoints: {int(len(payload.get('entrypoint_modules', [])))}",
        f"- Unreachable-from-entrypoints: {int(payload.get('unreachable_count', 0))}",
        f"- Cascade waves: {int(payload.get('cascade_wave_count', 0))}",
        f"- Cascade candidates: {int(payload.get('cascade_candidate_count', 0))}",
        "",
        "## How to use results",
        "",
        "- Unreachable-from-entrypoints: validate entrypoints + dynamic imports before removal.",
        "- Cascade waves: wave 0 is the safest starting point (orphan peel). Re-run after cleanup.",
        "- SCC clusters: treat each cluster as a unit when removing/refactoring mutually-referential modules.",
        "",
    ]

    missing = list(payload.get("missing_entrypoint_modules", []))
    lines.append("## Entrypoints")
    lines.append("")
    if not payload.get("entrypoint_modules"):
        lines.append("⚠️ No entrypoint modules configured; unreachable-from-entrypoints scan is skipped.")
    else:
        for m in payload.get("entrypoint_modules", []):
            lines.append(f"- `{m}`")
    lines.append("")
    if missing:
        lines.append("### Missing entrypoints (not found under root)")
        lines.append("")
        for m in missing:
            lines.append(f"- `{m}`")
        lines.append("")

    lines.append("## Cascade waves (orphan peel)")
    lines.append("")
    if not waves:
        lines.append("✅ None.")
        lines.append("")
    else:
        for i, wave in enumerate(waves):
            lines.append(f"### Wave {i} ({len(wave)})")
            lines.append("")
            for m in wave:
                p = module_to_file_path(root=Path(payload["root"]), module=m)
                lines.append(f"- `{m}`" if p is None else f"- `{m}` ({p.as_posix()})")
            lines.append("")

    lines.append("## Unreachable-from-entrypoints")
    lines.append("")
    if not payload.get("entrypoint_modules"):
        lines.append("⚠️ Skipped (no entrypoints configured).")
        lines.append("")
    elif not unreachable:
        lines.append("✅ None.")
        lines.append("")
    else:
        for m in unreachable:
            p = module_to_file_path(root=Path(payload["root"]), module=m)
            lines.append(f"- `{m}`" if p is None else f"- `{m}` ({p.as_posix()})")
        lines.append("")

    lines.append("## SCC clusters (cleanup units)")
    lines.append("")
    lines.append("### Cascade clusters")
    lines.append("")
    if not cs_clusters:
        lines.append("✅ None.")
        lines.append("")
    else:
        for c in cs_clusters:
            lines.append(f"- ({len(c)}) " + ", ".join(f"`{m}`" for m in c))
        lines.append("")

    lines.append("### Unreachable clusters")
    lines.append("")
    if not un_clusters:
        lines.append("✅ None.")
        lines.append("")
    else:
        for c in un_clusters:
            lines.append(f"- ({len(c)}) " + ", ".join(f"`{m}`" for m in c))
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {
        "md_path": str(md_path),
        "unreachable_count": int(payload.get("unreachable_count", 0)),
        "cascade_candidate_count": int(payload.get("cascade_candidate_count", 0)),
        "cascade_wave_count": int(payload.get("cascade_wave_count", 0)),
    }
    if write_json:
        json_path = output_dir / f"unreachable_module_detector_run_{generated}.json"
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out["json_path"] = str(json_path)
    return out


def main() -> int:
    _win_utf8_stdio()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory to scan for Python modules.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON config with entrypoints and allowlists.",
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
        help="Also write unreachable_module_detector_run_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded by analyzer collection).",
    )
    parser.add_argument(
        "--fail-on-unreachable",
        action="store_true",
        help="Exit with code 1 if unreachable_count exceeds --max-unreachable (default 0).",
    )
    parser.add_argument(
        "--max-unreachable",
        type=int,
        default=0,
        help="When using --fail-on-unreachable, allow up to this many unreachable modules (default: 0).",
    )
    parser.add_argument(
        "--fail-on-cascade",
        action="store_true",
        help="Exit with code 1 if cascade_candidate_count exceeds --max-cascade (default 0).",
    )
    parser.add_argument(
        "--max-cascade",
        type=int,
        default=0,
        help="When using --fail-on-cascade, allow up to this many cascade candidates (default: 0).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"❌ Root is not a directory: {root}", file=sys.stderr)
        return 2

    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    cfg = DeadFileConfig.load(args.config.resolve() if args.config else None)
    payload = _compute_run_payload(
        root=root,
        config=cfg,
        include_tests=bool(args.include_tests),
        generated=generated,
        workspace=workspace,
    )
    paths = _write_artifacts(output_dir=output_dir, payload=payload, write_json=bool(args.json))

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(
        "[SUMMARY] "
        f"unreachable={paths.get('unreachable_count', 0)} "
        f"cascade_candidates={paths.get('cascade_candidate_count', 0)} "
        f"cascade_waves={paths.get('cascade_wave_count', 0)}"
    )

    exit_code = 0
    if args.fail_on_unreachable:
        max_u = max(0, int(args.max_unreachable))
        ucount = int(payload.get("unreachable_count", 0))
        if ucount > max_u:
            print(
                f"❌ [FAIL] unreachable_count={ucount} exceeds --max-unreachable={max_u}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_cascade:
        max_c = max(0, int(args.max_cascade))
        ccount = int(payload.get("cascade_candidate_count", 0))
        if ccount > max_c:
            print(
                f"❌ [FAIL] cascade_candidate_count={ccount} exceeds --max-cascade={max_c}",
                file=sys.stderr,
            )
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

