#!/usr/bin/env python3
"""
Deep nesting detector (directory depth for code-containing folders).

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.deep_nesting_detector --help

Writes ``deep_nesting_scan_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``deep_nesting_scan.v1`` when ``--json`` is provided).
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
    "layers.layer_2_devtools.level_0_infra.level_0.path",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0" / "path",
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

_BASE_ANALYZER = _load_module_from_path(
    "_deep_nesting_detector_base_analyzer",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "base_health_analyzer.py",
)
sys.modules["layers.layer_2_devtools.level_0_infra.level_0"].BaseAnalyzer = _BASE_ANALYZER.BaseAnalyzer

_WORKSPACE = _load_module_from_path(
    "_deep_nesting_detector_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)
resolve_workspace_root = _WORKSPACE.resolve_workspace_root

_DEEP_NESTING = _load_module_from_path(
    "_deep_nesting_detector_analyzer",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_1"
    / "health_analyzers"
    / "deep_nesting.py",
)
DeepNestingAnalyzer = _DEEP_NESTING.DeepNestingAnalyzer


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _compute_payload(*, root: Path, generated: date, workspace: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "deep_nesting_scan.v1",
        "generated": generated.isoformat(),
        "workspace": workspace.as_posix(),
        "root": root.resolve().as_posix(),
    }
    payload["nesting"] = DeepNestingAnalyzer(root).analyze()
    return payload


def _write_artifacts(
    *,
    output_dir: Path,
    payload: dict[str, Any],
    write_json: bool,
    max_depth_override: int | None,
) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = str(payload["generated"])

    md_path = output_dir / f"deep_nesting_scan_{generated}.md"
    nesting = payload.get("nesting", {}) or {}
    max_depth = int(nesting.get("max_depth", 0))
    deep_dirs = nesting.get("deep_dirs", []) or []

    threshold = max_depth_override
    if threshold is None:
        threshold = 0

    offenders = (
        [d for d in deep_dirs if int(d.get("depth", 0)) > int(threshold)]
        if int(threshold) > 0
        else []
    )

    lines: list[str] = [
        "---",
        f"generated: {payload['generated']}",
        "artifact: deep_nesting_scan",
        f"schema: {payload['schema']}",
        f"root: {payload['root']}",
        "---",
        "",
        "# Deep nesting detector",
        "",
        f"- Root: `{payload['root']}`",
        f"- Max directory depth (code-containing dirs): {max_depth}",
        "",
    ]

    if max_depth_override is not None:
        lines.append(f"- Threshold (override): depth > {int(max_depth_override)}")
        lines.append(f"- Offending directories: {len(offenders)}")
        lines.append("")

    lines.append("## Deepest directories")
    lines.append("")
    if not deep_dirs:
        lines.append("✅ None (no Python files found under root).")
        lines.append("")
    else:
        for row in deep_dirs[:50]:
            d = row.get("dir", "<?>")
            depth = int(row.get("depth", 0))
            py_files = int(row.get("py_files", 0))
            lines.append(f"- depth {depth} `{d}` ({py_files} .py files)")
        if len(deep_dirs) > 50:
            lines.append(f"- ... and {len(deep_dirs) - 50} more")
        lines.append("")

    if max_depth_override is not None:
        lines.append("## Offenders (threshold override)")
        lines.append("")
        if not offenders:
            lines.append("✅ None.")
            lines.append("")
        else:
            for row in offenders[:50]:
                d = row.get("dir", "<?>")
                depth = int(row.get("depth", 0))
                py_files = int(row.get("py_files", 0))
                lines.append(f"- depth {depth} `{d}` ({py_files} .py files)")
            if len(offenders) > 50:
                lines.append(f"- ... and {len(offenders) - 50} more")
            lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {
        "md_path": str(md_path),
        "max_depth": int(max_depth),
        "deep_dir_count": int(len(deep_dirs)),
        "offender_count": int(len(offenders)),
    }

    if write_json:
        json_path = output_dir / f"deep_nesting_scan_{generated}.json"
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out["json_path"] = str(json_path)
    return out


def main() -> int:
    _win_utf8_stdio()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to analyze.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional threshold override for reporting offenders (depth > max-depth).",
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
        help="Also write deep_nesting_scan_<date>.json next to the .md report.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"❌ Root is not a directory: {root}", file=sys.stderr)
        return 2

    if args.max_depth is not None and int(args.max_depth) < 0:
        print("❌ --max-depth must be >= 0", file=sys.stderr)
        return 2

    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    payload = _compute_payload(root=root, generated=generated, workspace=workspace)
    paths = _write_artifacts(
        output_dir=output_dir,
        payload=payload,
        write_json=bool(args.json),
        max_depth_override=args.max_depth,
    )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(
        "[SUMMARY] "
        f"max_depth={paths.get('max_depth', 0)} "
        f"dirs={paths.get('deep_dir_count', 0)} "
        f"offenders={paths.get('offender_count', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

