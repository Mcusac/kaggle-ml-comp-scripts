#!/usr/bin/env python3
"""
Dead symbol detector (orchestrator).

Runs both:
- unreferenced scan
- unreachable-from-entrypoints scan

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.dead_symbol_detector --help

Writes ``dead_symbol_detector_run_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``dead_symbol_detector_run.v1`` when ``--json`` is provided).
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


def _reachable(*, edges: dict[str, set[str]], entrypoints: set[str]) -> set[str]:
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


def _compute_run_payload(
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
    def_span: dict[str, tuple[int, int]] = {}
    spans_by_module: dict[str, list[tuple[str, int, int]]] = {}
    all_defs: set[str] = set()
    for d in defs:
        defs_by_module.setdefault(d.module, set()).add(d.qualname)
        all_defs.add(d.symbol_id)
        def_span[d.symbol_id] = (int(d.line_start), int(d.line_end))
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

    referenced: set[str] = set()
    edges: dict[str, set[str]] = {sid: set() for sid in all_defs}
    incoming: dict[str, set[str]] = {}

    for r in refs:
        target = r.resolved_symbol_id
        if target not in all_defs:
            continue
        if target in config.allow_symbol_ids:
            continue

        span = def_span.get(target)
        if span is not None:
            start, end = span
            if r.ref_module == target.split(":", 1)[0] and start <= r.line <= end:
                # Self-reference inside its own definition span does not count as “referenced”.
                pass
            else:
                referenced.add(target)
        else:
            referenced.add(target)

        src = None
        spans = spans_by_module.get(r.ref_module, [])
        if spans and r.line:
            containing = [s for s in spans if s[1] <= r.line <= s[2]]
            if containing:
                containing.sort(key=lambda x: (x[2] - x[1], x[1]))
                src = containing[0][0]
        if src is None:
            src = f"{r.ref_module}:__module__"

        edges.setdefault(src, set()).add(target)
        incoming.setdefault(target, set()).add(src)

    unreferenced = sorted(
        sid
        for sid in all_defs
        if sid not in referenced and sid not in config.allow_symbol_ids
    )

    entrypoints: set[str] = set(config.entrypoint_symbol_ids)
    if not entrypoints:
        entrypoints = {sid for sid, inc in incoming.items() if inc}

    reachable = _reachable(edges=edges, entrypoints=entrypoints)
    unreachable = sorted(
        sid
        for sid in all_defs
        if sid not in reachable and sid not in config.allow_symbol_ids
    )

    return {
        "schema": "dead_symbol_detector_run.v1",
        "generated": generated.isoformat(),
        "workspace": workspace.as_posix(),
        "root": root.resolve().as_posix(),
        "include_tests": bool(include_tests),
        "definition_count": int(len(all_defs)),
        "reference_count": int(len(refs)),
        "unreferenced_count": int(len(unreferenced)),
        "unreachable_count": int(len(unreachable)),
        "entrypoint_count": int(len(entrypoints)),
        "entrypoint_symbol_ids": sorted(entrypoints),
        "unreferenced_symbol_ids": list(unreferenced),
        "unreachable_symbol_ids": list(unreachable),
    }


def _write_artifacts(*, output_dir: Path, payload: dict, write_json: bool) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = str(payload["generated"])
    md_path = output_dir / f"dead_symbol_detector_run_{generated}.md"

    unref = list(payload.get("unreferenced_symbol_ids", []))
    unrch = list(payload.get("unreachable_symbol_ids", []))

    lines: list[str] = [
        "---",
        f"generated: {payload['generated']}",
        "artifact: dead_symbol_detector_run",
        f"schema: {payload['schema']}",
        f"root: {payload['root']}",
        "---",
        "",
        "# Dead symbol detector",
        "",
        f"- Root: `{payload['root']}`",
        f"- Include tests: {bool(payload['include_tests'])}",
        f"- Definitions: {int(payload['definition_count'])}",
        f"- Resolved references: {int(payload['reference_count'])}",
        f"- Entrypoints: {int(payload['entrypoint_count'])}",
        f"- Unreferenced: {int(payload['unreferenced_count'])}",
        f"- Unreachable: {int(payload['unreachable_count'])}",
        "",
        "## How to use results",
        "",
        "- Unreferenced: remove the symbol, make it private, or add it to allowlist if used dynamically.",
        "- Unreachable: verify entrypoints config; then remove or refactor the unreachable cluster.",
        "",
    ]

    lines.append("## Unreferenced symbols")
    lines.append("")
    if not unref:
        lines.append("✅ None.")
        lines.append("")
    else:
        for sym in unref:
            lines.append(f"- `{sym}`")
        lines.append("")

    lines.append("## Unreachable symbols")
    lines.append("")
    if not unrch:
        lines.append("✅ None.")
        lines.append("")
    else:
        for sym in unrch:
            lines.append(f"- `{sym}`")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {
        "md_path": str(md_path),
        "definition_count": int(payload.get("definition_count", 0)),
        "reference_count": int(payload.get("reference_count", 0)),
        "unreferenced_count": int(payload.get("unreferenced_count", 0)),
        "unreachable_count": int(payload.get("unreachable_count", 0)),
    }

    if write_json:
        json_path = output_dir / f"dead_symbol_detector_run_{generated}.json"
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
        help="Also write dead_symbol_detector_run_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include `tests/` directories and test_*.py modules (default: excluded).",
    )
    parser.add_argument(
        "--fail-on-unreferenced",
        action="store_true",
        help="Exit 1 if unreferenced_count exceeds --max-unreferenced (default 0).",
    )
    parser.add_argument(
        "--max-unreferenced",
        type=int,
        default=0,
        help="When using --fail-on-unreferenced, allow up to this many unreferenced symbols (default: 0).",
    )
    parser.add_argument(
        "--fail-on-unreachable",
        action="store_true",
        help="Exit 1 if unreachable_count exceeds --max-unreachable (default 0).",
    )
    parser.add_argument(
        "--max-unreachable",
        type=int,
        default=0,
        help="When using --fail-on-unreachable, allow up to this many unreachable symbols (default: 0).",
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

    payload = _compute_run_payload(
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
        f"unreferenced={paths['unreferenced_count']} "
        f"unreachable={paths['unreachable_count']}"
    )

    exit_code = 0
    if args.fail_on_unreferenced:
        max_u = max(0, int(args.max_unreferenced))
        ucount = int(paths.get("unreferenced_count", 0))
        if ucount > max_u:
            print(
                f"❌ [FAIL] unreferenced_count={ucount} exceeds --max-unreferenced={max_u}",
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

