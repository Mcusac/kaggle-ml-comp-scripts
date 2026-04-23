#!/usr/bin/env python3
"""
Dead file detector for Python modules under a chosen root.

Reports:
- Orphaned modules: internal modules with no incoming internal imports (excluding allowlist)
- Unreachable modules: internal modules not reachable from configured entrypoint modules

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python layers/layer_2_devtools/level_1_impl/level_2/dead_file_detector.py --help

Writes ``dead_file_detector_run_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``dead_file_detector_run.v1`` when ``--json`` is provided).
"""

from __future__ import annotations

import argparse
import io
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Any

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]


def _load_module_from_path(name: str, path: Path):
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
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.path",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0" / "path",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra.level_0.models",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "models",
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


_DEAD_FILE_CONFIG = _load_module_from_path(
    "_dead_file_detector_dead_file_config",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "models"
    / "dead_file_config.py",
)
_PYMODS = _load_module_from_path(
    "_dead_file_detector_pymods",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "python_modules.py",
)
_WORKSPACE = _load_module_from_path(
    "_dead_file_detector_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)
_IMPORT_ANALYZER = _load_module_from_path(
    "_dead_file_detector_import_analyzer",
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


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


_REACHABILITY = _load_module_from_path(
    "_dead_file_detector_reachability",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "graph"
    / "reachability.py",
)

reachable_from_entrypoints = _REACHABILITY.reachable_from_entrypoints


def _compute_candidates(
    *,
    root: Path,
    config: DeadFileConfig,
    include_tests: bool,
) -> dict[str, Any]:
    # ImportAnalyzer already encapsulates “intentional orphan” exclusions for the orphan list.
    imports = ImportAnalyzer(root).analyze()

    internal_packages = discover_packages(root)
    import_map = imports.get("import_map", {}) or {}
    all_modules = sorted([m for m in import_map.keys() if is_internal_module(m, internal_packages)])

    allow_modules = set(config.allow_modules)
    allow_prefixes = tuple(config.allow_module_prefixes)

    def allowed(m: str) -> bool:
        if not m:
            return True
        if m in allow_modules:
            return True
        return any(m.startswith(pfx) for pfx in allow_prefixes)

    orphans = [m for m in list(imports.get("orphans", []) or []) if isinstance(m, str)]
    entrypoints = set(config.entrypoint_modules)
    orphans = sorted([m for m in orphans if m not in entrypoints and not allowed(m)])

    unreachable: list[str] = []
    if entrypoints:
        reachable = reachable_from_entrypoints(graph=import_map, entrypoints=entrypoints)
        unreachable = sorted([m for m in all_modules if m not in reachable and not allowed(m)])

    missing_entrypoints = sorted([m for m in entrypoints if m not in set(all_modules)])

    return {
        "schema": "dead_file_detector_run.v1",
        "root": root.resolve().as_posix(),
        "include_tests": bool(include_tests),
        "entrypoint_modules": sorted(entrypoints),
        "missing_entrypoint_modules": missing_entrypoints,
        "orphan_modules": orphans,
        "unreachable_modules": unreachable,
        "orphan_count": int(len(orphans)),
        "unreachable_count": int(len(unreachable)),
    }


def _write_artifacts(*, output_dir: Path, payload: dict[str, Any], generated: date, write_json: bool) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"dead_file_detector_run_{generated.isoformat()}.md"

    orphans = list(payload.get("orphan_modules", []))
    unreachable = list(payload.get("unreachable_modules", []))
    entrypoints = list(payload.get("entrypoint_modules", []))
    missing_entrypoints = list(payload.get("missing_entrypoint_modules", []))

    lines: list[str] = [
        "---",
        f"generated: {generated.isoformat()}",
        "artifact: dead_file_detector_run",
        f"schema: {payload.get('schema', 'dead_file_detector_run.v1')}",
        f"root: {payload.get('root', '')}",
        "---",
        "",
        "# Dead file detector",
        "",
        f"- Root: `{payload.get('root', '')}`",
        f"- Orphaned modules: {int(payload.get('orphan_count', 0))}",
        f"- Unreachable modules: {int(payload.get('unreachable_count', 0))}",
        "",
        "## How to use results",
        "",
        "- Orphaned: module has no incoming internal imports; validate it is not a CLI/registry/dynamic entrypoint.",
        "- Unreachable: module is not reachable from configured entrypoint modules; validate entrypoints config and any dynamic imports before removal.",
        "",
    ]

    lines.append("## Entrypoints")
    lines.append("")
    if not entrypoints:
        lines.append("⚠️ No entrypoint modules configured; unreachable scan is skipped.")
        lines.append("")
    else:
        for m in entrypoints:
            lines.append(f"- `{m}`")
        lines.append("")
    if missing_entrypoints:
        lines.append("### Missing entrypoints (not found under root)")
        lines.append("")
        for m in missing_entrypoints:
            lines.append(f"- `{m}`")
        lines.append("")

    lines.append("## Orphaned modules")
    lines.append("")
    if not orphans:
        lines.append("✅ None.")
        lines.append("")
    else:
        for m in orphans:
            p = module_to_file_path(root=Path(payload["root"]), module=m)
            if p is None:
                lines.append(f"- `{m}`")
            else:
                lines.append(f"- `{m}` ({p.as_posix()})")
        lines.append("")

    lines.append("## Unreachable modules")
    lines.append("")
    if not entrypoints:
        lines.append("⚠️ Skipped (no entrypoints configured).")
        lines.append("")
    elif not unreachable:
        lines.append("✅ None.")
        lines.append("")
    else:
        for m in unreachable:
            p = module_to_file_path(root=Path(payload["root"]), module=m)
            if p is None:
                lines.append(f"- `{m}`")
            else:
                lines.append(f"- `{m}` ({p.as_posix()})")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {
        "md_path": str(md_path),
        "orphan_count": int(payload.get("orphan_count", 0)),
        "unreachable_count": int(payload.get("unreachable_count", 0)),
    }
    if write_json:
        json_path = output_dir / f"dead_file_detector_run_{generated.isoformat()}.json"
        json_payload = dict(payload)
        json_payload["generated"] = generated.isoformat()
        json_path.write_text(
            json.dumps(json_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
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
        help="Also write dead_file_detector_run_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded by analyzer collection).",
    )
    parser.add_argument(
        "--fail-on-orphans",
        action="store_true",
        help="Exit with code 1 if orphan_count exceeds --max-orphans (default 0).",
    )
    parser.add_argument(
        "--max-orphans",
        type=int,
        default=0,
        help="When using --fail-on-orphans, allow up to this many orphans (default: 0).",
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
    payload = _compute_candidates(
        root=root,
        config=cfg,
        include_tests=bool(args.include_tests),
    )
    payload["generated"] = generated.isoformat()
    payload["workspace"] = workspace.as_posix()

    paths = _write_artifacts(
        output_dir=output_dir,
        payload=payload,
        generated=generated,
        write_json=bool(args.json),
    )

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(
        "[SUMMARY] "
        f"orphans={paths.get('orphan_count', 0)} "
        f"unreachable={paths.get('unreachable_count', 0)}"
    )

    exit_code = 0
    if args.fail_on_orphans:
        max_o = max(0, int(args.max_orphans))
        ocount = int(paths.get("orphan_count", 0))
        if ocount > max_o:
            print(
                f"❌ [FAIL] orphan_count={ocount} exceeds --max-orphans={max_o}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_unreachable:
        max_u = max(0, int(args.max_unreachable))
        ucount = int(paths.get("unreachable_count", 0))
        if ucount > max_u:
            print(
                f"❌ [FAIL] unreachable_count={ucount} exceeds --max-unreachable={max_u}",
                file=sys.stderr,
            )
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

