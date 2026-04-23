"""Public API: thin script orchestration (cleanup, bootstrap, one-off fixers)."""

import sys

import json
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok
from layers.layer_2_devtools.level_0_infra.level_0.fix.layer_core_import_rewrite import (
    run_layer_core_import_rewrite,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.import_fix_strategies import (
    FixOptions,
    build_edit_operations_for_tree,
    iter_python_files,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.import_rewrite_engine import (
    apply_edit_operations,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.text_span_rewrite_engine import (
    SpanEditOperation,
    apply_span_edit_operations,
)
from layers.layer_2_devtools.level_0_infra.level_0 import (
    run_unused_import_cleanup,
)
from layers.layer_2_devtools.level_0_infra.level_0 import (
    run_violation_fix_bundle,
)
from layers.layer_2_devtools.level_0_infra.level_0 import (
    bootstrap_markdown,
)
from layers.layer_2_devtools.level_0_infra.level_0 import clean_pycache
from layers.layer_2_devtools.level_0_infra.level_1 import dump_level
from layers.layer_2_devtools.level_0_infra.level_1 import package_dump_main
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import (
    resolve_workspace_root,
)
from layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.import_path_validator import (
    ImportPathValidator,
)
from layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.import_surface_validator import (
    ImportSurfaceValidator,
)
from layers.layer_2_devtools.level_0_infra.level_0.formatting.import_organizer import (
    build_import_organizer_span_edit,
)


def run_unused_import_cleanup_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``report``, ``root``, ``dry_run``, optional formatting flags."""
    try:
        rep = config.get("report")
        if rep is None:
            return err(["report is required"])
        rc = run_unused_import_cleanup(
            report=Path(rep),
            root=Path(config.get("root", Path.cwd())),
            dry_run=bool(config.get("dry_run", False)),
            organize_imports=bool(config.get("organize_imports", True)),
            format_after=bool(config.get("format_after", False)),
            format_tool=str(config.get("format_tool", "ruff")),
            format_args=list(config.get("format_args") or []),
        )
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_clean_pycache_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``root``, ``dry_run``, ``remove_pyc_files``."""
    try:
        root = Path(config.get("root", Path.cwd()))
        if not root.is_dir():
            return err([f"root is not a directory: {root}"])
        dry = bool(config.get("dry_run", False))
        result = clean_pycache(
            root,
            dry_run=dry,
            remove_pyc_files=bool(config.get("remove_pyc_files", False)),
        )
        if dry:
            msg = (
                f"Dry run: would remove {result.dirs_removed} __pycache__ dirs and "
                f"{result.files_removed} .pyc files."
            )
        else:
            msg = (
                f"Removed {result.dirs_removed} __pycache__ dirs and "
                f"{result.files_removed} .pyc files."
            )
        return ok({"exit_code": 0, "message": msg})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_inventory_bootstrap_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``level_path``, optional ``workspace_root``, ``output`` (Path or None)."""
    try:
        lp = config.get("level_path")
        if lp is None:
            return err(["level_path is required"])
        ws = Path(config["workspace_root"]).resolve() if config.get("workspace_root") else None
        body = bootstrap_markdown(Path(lp), ws)
        out = config.get("output")
        wrote = False
        if out:
            outp = Path(out)
            outp.parent.mkdir(parents=True, exist_ok=True)
            outp.write_text(body, encoding="utf-8")
            wrote = True
        return ok({"body": body, "output_path": str(out) if out else None, "wrote_file": wrote})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_layer_core_import_rewrite_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: optional ``layer_0_core`` Path (default: scripts_root/layers/layer_0_core)."""
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return err(["scripts_root is required"])
        core = config.get("layer_0_core")
        scripts_root = Path(sr)
        target = Path(core).resolve() if core else (scripts_root / "layers" / "layer_0_core")
        rc = run_layer_core_import_rewrite(target)
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_violation_fix_bundle_standalone_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``scripts_dev_dir``, ``apply`` (bool)."""
    try:
        sdd = config.get("scripts_dev_dir")
        if sdd is None:
            return err(["scripts_dev_dir is required"])
        dry_run = not bool(config.get("apply", False))
        run_violation_fix_bundle(Path(sdd), dry_run)
        return ok({})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_fix_imports_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Rewrite-only import auto-fixer.

    Config:
        - scripts_root (Path-like, required): directory containing `layers/`
        - root (Path-like, optional): tree to scan; default `scripts_root/layers`
        - apply (bool): default False (dry-run)
        - include_tests (bool): default False
        - rewrite_relative_in_logic (str): "off" or "absolute" (default "off")
        - max_changes_per_file (int): default 25
    """
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return err(["scripts_root is required"])
        scripts_root = Path(sr).resolve()
        root = Path(config.get("root") or (scripts_root / "layers")).resolve()
        if not root.is_dir():
            return err([f"root is not a directory: {root}"])

        apply = bool(config.get("apply", False))
        include_tests = bool(config.get("include_tests", False))
        rewrite_relative_in_logic = str(config.get("rewrite_relative_in_logic", "off"))
        max_changes_per_file = int(config.get("max_changes_per_file", 25) or 25)
        if rewrite_relative_in_logic not in ("off", "absolute"):
            return err([f"rewrite_relative_in_logic must be 'off' or 'absolute', got: {rewrite_relative_in_logic}"])

        ops, build_errors = build_edit_operations_for_tree(
            root=root,
            scripts_root=scripts_root,
            opts=FixOptions(
                include_tests=include_tests,
                rewrite_relative_in_logic=rewrite_relative_in_logic,
            ),
        )
        results, summary, apply_errors = apply_edit_operations(
            ops,
            apply=apply,
            max_changes_per_file=max(0, int(max_changes_per_file)),
        )
        errors = list(build_errors) + list(apply_errors)
        status = ok(
            {
                "files_considered": summary.files_considered,
                "files_changed": summary.files_changed,
                "edits_applied": summary.edits_applied,
                "changed_files": [
                    {"path": r.path.as_posix(), "edits": int(r.edits_applied)}
                    for r in results
                    if r.edits_applied
                ],
            }
        )
        if errors:
            # keep envelope shape but surface warnings
            status["data"]["warnings"] = errors
        return status
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_import_organizer_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Organize top-of-file imports per `python-import-order.mdc` (rewrite-only).

    Config:
        - root (Path-like, required): tree to scan
        - apply (bool): default False (dry-run)
        - include_tests (bool): include test_*.py (default False)
        - max_changes_per_file (int): safety cap; default 1
        - max_files (int|None): optional limit on number of files processed
    """
    try:
        root_raw = config.get("root")
        if root_raw is None:
            return err(["root is required"])
        root = Path(root_raw).resolve()
        if not root.is_dir():
            return err([f"root is not a directory: {root}"])

        apply = bool(config.get("apply", False))
        include_tests = bool(config.get("include_tests", False))
        max_changes_per_file = int(config.get("max_changes_per_file", 1) or 1)
        max_files_raw = config.get("max_files")
        max_files = int(max_files_raw) if max_files_raw is not None else None

        opts = FixOptions(include_tests=include_tests)
        paths = iter_python_files(root, include_tests=opts.include_tests)
        if max_files is not None:
            paths = paths[: max(0, int(max_files))]

        ops: list[SpanEditOperation] = []
        warnings: list[str] = []
        for p in paths:
            res = build_import_organizer_span_edit(p)
            warnings.extend(res.warnings)
            if res.op is not None:
                ops.append(res.op)

        results, summary, apply_errors = apply_span_edit_operations(
            ops,
            apply=apply,
            max_changes_per_file=max(1, int(max_changes_per_file)),
        )
        warnings.extend(apply_errors)
        return ok(
            {
                "files_considered": summary.files_considered,
                "files_changed": summary.files_changed,
                "edits_applied": summary.edits_applied,
                "changed_files": sorted(
                    {r.path.as_posix() for r in results if r.applied}
                ),
                "warnings": warnings,
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_package_dump_sys_argv_api(argv: list[str]) -> dict[str, Any]:
    """Invoke package dump CLI with a replacement ``sys.argv`` (excluding prog)."""
    old = sys.argv
    try:
        sys.argv = [old[0], *argv]
        rc = package_dump_main()
        return ok({"exit_code": int(rc)})
    except SystemExit as exc:  # argparse may raise
        code = exc.code
        if isinstance(code, int):
            return ok({"exit_code": code})
        return err([str(code) if code else "package_dump exited"])
    finally:
        sys.argv = old


def run_dump_level_preset_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Config: ``level_name``, ``scripts_root``, optional ``output_dir`` (default package_dumps)."""
    try:
        name = config.get("level_name")
        sr = config.get("scripts_root")
        if name is None or sr is None:
            return err(["level_name and scripts_root are required"])
        layer0 = Path(sr) / "layers" / "layer_0_core"
        od = Path(config.get("output_dir", "package_dumps"))
        dump_level(str(name), scripts_root=layer0, output_dir=od)
        return ok({})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_verify_imports_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Verify import policies and module resolution (filesystem + AST).

    Config:
        - scripts_root (Path-like, required): directory containing `layers/`
        - root (Path-like, optional): tree to scan; default `scripts_root/layers/layer_0_core`
        - output_dir (Path-like, optional): default `<workspace>/.cursor/audit-results/general/audits`
        - generated (date or YYYY-MM-DD, optional): for artifact filenames; default today
        - include_tests (bool): include test_*.py (default False)
        - write_json (bool): write JSON payload next to markdown (default False)
    """
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return err(["scripts_root is required"])
        scripts_root = Path(sr).resolve()
        root = Path(config.get("root") or (scripts_root / "layers" / "layer_0_core")).resolve()
        if not root.is_dir():
            return err([f"root is not a directory: {root}"])

        generated = config.get("generated")
        if generated is None:
            gen = date.today()
        elif isinstance(generated, date):
            gen = generated
        else:
            gen = date.fromisoformat(str(generated))

        workspace = resolve_workspace_root(root)
        output_dir = (
            Path(config["output_dir"]).resolve()
            if config.get("output_dir")
            else (workspace / ".cursor" / "audit-results" / "general" / "audits")
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        include_tests = bool(config.get("include_tests", False))
        write_json = bool(config.get("write_json", False))

        surface = ImportSurfaceValidator(root, include_tests=include_tests).analyze()
        rel = ImportPathValidator(root, include_tests=include_tests).analyze()

        violations = list(surface.get("violations", []))
        for row in rel.get("invalid_imports", []):
            violations.append(
                {
                    "file": row.get("file", ""),
                    "line": int(row.get("line", 0) or 0),
                    "kind": "RELATIVE_IMPORT_UNRESOLVED",
                    "module": row.get("resolved", ""),
                    "name": None,
                    "message": "Relative import does not resolve to an internal module.",
                    "suggested": row.get("suggested"),
                }
            )

        payload: dict[str, Any] = {
            "schema": "verify_imports_scan.v1",
            "generated": gen.isoformat(),
            "workspace": workspace.as_posix(),
            "root": root.as_posix(),
            "include_tests": bool(include_tests),
            "parse_error_count": int(surface.get("parse_error_count", 0) or 0),
            "violation_count": int(len(violations)),
            "violations": violations,
        }

        md_path = output_dir / f"verify_imports_scan_{gen.isoformat()}.md"
        lines: list[str] = [
            "---",
            f"generated: {gen.isoformat()}",
            "artifact: verify_imports_scan",
            "schema: verify_imports_scan.v1",
            f"root: {root.as_posix()}",
            "---",
            "",
            "# Import verification (strict policy)",
            "",
            f"- Root: `{root.as_posix()}`",
            f"- Violations: {payload['violation_count']}",
            f"- Parse errors: {payload['parse_error_count']}",
            "",
        ]
        if not violations:
            lines.append("✅ No import policy violations detected.")
            lines.append("")
        else:
            lines.append("## Violations")
            lines.append("")
            for idx, v in enumerate(violations, start=1):
                f = v.get("file", "")
                ln = int(v.get("line", 0) or 0)
                kind = v.get("kind", "")
                mod = v.get("module", "")
                msg = v.get("message", "")
                sug = v.get("suggested")
                lines.append(f"{idx}. **{kind}** — `{f}`:{ln}")
                if mod:
                    lines.append(f"   - Module: `{mod}`")
                if msg:
                    lines.append(f"   - Message: {msg}")
                if sug:
                    lines.append(f"   - Suggested: `{sug}`")
            lines.append("")

        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        out: dict[str, Any] = {
            "exit_code": 0,
            "md_path": str(md_path),
            "payload": payload,
            "violation_count": int(payload["violation_count"]),
            "parse_error_count": int(payload["parse_error_count"]),
            "summary_line": (
                f"[SUMMARY] violations={payload['violation_count']} "
                f"parse_errors={payload['parse_error_count']}"
            ),
        }
        if write_json:
            json_path = output_dir / f"verify_imports_scan_{gen.isoformat()}.json"
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            out["json_path"] = str(json_path)
        return ok(out)
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_verify_imports_stub_api(config: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible alias for callers that haven't migrated."""
    return run_verify_imports_cli_api(config)