#!/usr/bin/env python3
"""
Dead symbol detector (unreachable-from-entrypoints).

Builds a conservative symbol-to-symbol dependency graph from resolved references and
marks symbols unreachable from configured entrypoints.

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.dead_symbols_unreachable --help

Writes ``dead_symbols_unreachable_scan_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``dead_symbols_unreachable_scan.v1`` when ``--json`` is provided).
"""

import argparse
import io
import json
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]


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

from layers.layer_2_devtools.level_0_infra.level_0.models.dead_symbol_config import (  # noqa: E402
    DeadSymbolConfig,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.symbol_definition_index import (  # noqa: E402
    DefinitionIndexBuilder,
    DefinitionIndexOptions,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.symbol_reference_index import (  # noqa: E402
    ReferenceIndexBuilder,
    ReferenceIndexOptions,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import (  # noqa: E402
    resolve_workspace_root,
)


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _reachable(
    *,
    edges: dict[str, set[str]],
    entrypoints: set[str],
) -> set[str]:
    seen: set[str] = set()
    stack = list(sorted(entrypoints))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for nxt in sorted(edges.get(cur, set())):
            if nxt not in seen:
                stack.append(nxt)
    return seen


def _compute_unreachable_payload(
    *,
    root: Path,
    include_tests: bool,
    config: DeadSymbolConfig,
    generated: date,
    workspace: Path,
) -> dict:
    defs = DefinitionIndexBuilder(
        DefinitionIndexOptions(root=root, include_tests=include_tests)
    ).build()
    defs = [d for d in defs if d.module not in config.allow_modules]

    defs_by_module: dict[str, set[str]] = {}
    all_defs: set[str] = set()
    spans_by_module: dict[str, list[tuple[str, int, int]]] = {}
    for d in defs:
        defs_by_module.setdefault(d.module, set()).add(d.qualname)
        all_defs.add(d.symbol_id)
        spans_by_module.setdefault(d.module, []).append(
            (d.symbol_id, int(d.line_start), int(d.line_end))
        )

    for mod, spans in spans_by_module.items():
        spans_by_module[mod] = sorted(spans, key=lambda x: (x[1], x[2], x[0]))

    refs = ReferenceIndexBuilder(
        ReferenceIndexOptions(
            root=root,
            definitions_by_module=defs_by_module,
            include_tests=include_tests,
        )
    ).build()

    # Edges are computed at symbol granularity using resolved_symbol_id, limited to known defs.
    edges: dict[str, set[str]] = {sid: set() for sid in all_defs}
    incoming: dict[str, set[str]] = {}

    for r in refs:
        target = r.resolved_symbol_id
        if target not in all_defs:
            continue
        if target in config.allow_symbol_ids:
            continue

        src = None
        spans = spans_by_module.get(r.ref_module, [])
        if spans and r.line:
            containing = [s for s in spans if s[1] <= r.line <= s[2]]
            if containing:
                # Prefer the most specific (smallest span).
                containing.sort(key=lambda x: (x[2] - x[1], x[1]))
                src = containing[0][0]
        if src is None:
            src = f"{r.ref_module}:__module__"
        edges.setdefault(src, set()).add(target)
        incoming.setdefault(target, set()).add(src)

    entrypoints: set[str] = set(config.entrypoint_symbol_ids)

    # Default heuristic: when no explicit entrypoints are provided, seed reachability from
    # any symbol that has at least one incoming reference from a different module.
    if not entrypoints:
        entrypoints = {sid for sid, inc in incoming.items() if inc}

    reachable = _reachable(edges=edges, entrypoints=entrypoints)

    dead = sorted(
        sid
        for sid in all_defs
        if sid not in reachable and sid not in config.allow_symbol_ids
    )

    return {
        "schema": "dead_symbols_unreachable_scan.v1",
        "generated": generated.isoformat(),
        "workspace": workspace.as_posix(),
        "root": root.resolve().as_posix(),
        "include_tests": bool(include_tests),
        "definition_count": int(len(all_defs)),
        "reference_count": int(len(refs)),
        "entrypoint_count": int(len(entrypoints)),
        "reachable_count": int(len(reachable & all_defs)),
        "dead_count": int(len(dead)),
        "entrypoint_symbol_ids": sorted(entrypoints),
        "dead_symbol_ids": list(dead),
    }


def _write_artifacts(*, output_dir: Path, payload: dict, write_json: bool) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = str(payload["generated"])
    md_path = output_dir / f"dead_symbols_unreachable_scan_{generated}.md"

    dead = list(payload.get("dead_symbol_ids", []))

    lines: list[str] = [
        "---",
        f"generated: {payload['generated']}",
        "artifact: dead_symbols_unreachable_scan",
        f"schema: {payload['schema']}",
        f"root: {payload['root']}",
        "---",
        "",
        "# Dead symbols (unreachable-from-entrypoints)",
        "",
        f"- Root: `{payload['root']}`",
        f"- Include tests: {bool(payload['include_tests'])}",
        f"- Definitions: {int(payload['definition_count'])}",
        f"- Resolved references: {int(payload['reference_count'])}",
        f"- Entrypoints: {int(payload['entrypoint_count'])}",
        f"- Reachable definitions: {int(payload['reachable_count'])}",
        f"- Dead symbols: {int(payload['dead_count'])}",
        "",
    ]

    if not dead:
        lines.append("✅ No unreachable symbols detected.")
        lines.append("")
    else:
        lines.append("## Dead symbol IDs")
        lines.append("")
        for sym in dead:
            lines.append(f"- `{sym}`")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {
        "md_path": str(md_path),
        "dead_count": int(payload.get("dead_count", 0)),
        "definition_count": int(payload.get("definition_count", 0)),
        "reference_count": int(payload.get("reference_count", 0)),
        "entrypoint_count": int(payload.get("entrypoint_count", 0)),
    }

    if write_json:
        json_path = output_dir / f"dead_symbols_unreachable_scan_{generated}.json"
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
        help="Root directory to scan (e.g. scripts/layers/layer_0_core).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON config with allowlists and entrypoints.",
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
        help="Also write dead_symbols_unreachable_scan_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include `tests/` directories and test_*.py modules (default: excluded).",
    )
    parser.add_argument(
        "--fail-on-dead",
        action="store_true",
        help="Exit with code 1 if dead_count exceeds --max-dead (default 0).",
    )
    parser.add_argument(
        "--max-dead",
        type=int,
        default=0,
        help="When using --fail-on-dead, allow up to this many dead symbols (default: 0).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        print(f"❌ Root does not exist: {root}", file=sys.stderr)
        return 2

    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    cfg = DeadSymbolConfig.load(args.config.resolve() if args.config else None)

    payload = _compute_unreachable_payload(
        root=root,
        include_tests=bool(args.include_tests),
        config=cfg,
        generated=generated,
        workspace=workspace,
    )
    paths = _write_artifacts(output_dir=output_dir, payload=payload, write_json=bool(args.json))

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(
        "[SUMMARY] "
        f"defs={paths['definition_count']} "
        f"refs={paths['reference_count']} "
        f"entrypoints={paths['entrypoint_count']} "
        f"dead={paths['dead_count']}"
    )

    if args.fail_on_dead:
        max_dead = max(0, int(args.max_dead))
        dead_count = int(paths.get("dead_count", 0))
        if dead_count > max_dead:
            print(
                f"❌ [FAIL] dead_count={dead_count} exceeds --max-dead={max_dead}",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

