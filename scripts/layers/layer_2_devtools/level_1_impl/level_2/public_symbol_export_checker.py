#!/usr/bin/env python3
"""
Public symbol export checker for Python packages under a chosen root.

This tool answers: which public top-level symbols (per deterministic rules) exist in leaf
modules but are not exported by the owning package's `__init__.py` surface (`__all__` and
relative re-exports).

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.public_symbol_export_checker --help

Writes ``public_symbol_export_check_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default (JSON schema:
``public_symbol_export_check.v1`` when ``--json`` is provided).
"""

from __future__ import annotations

import argparse
import ast
import io
import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Avoid importing `level_0_infra` package trees here (optional deps). Load `workspace.py` directly.
def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_WORKSPACE = _load_module_from_path(
    "_public_symbol_export_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)
resolve_workspace_root = _WORKSPACE.resolve_workspace_root

# Avoid importing `level_1_impl.level_0` package trees here (they can transitively pull optional deps).
_REGEN_ROOT = (
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_0"
    / "regenerate_inits"
)
_PUBLIC_SYMBOLS = _load_module_from_path(
    "_public_symbol_export_public_symbols", _REGEN_ROOT / "public_symbols.py"
)
_WALK = _load_module_from_path("_public_symbol_export_walk", _REGEN_ROOT / "walk.py")

public_symbols_from_file = _PUBLIC_SYMBOLS.public_symbols_from_file
bottom_up_package_dirs = _WALK.bottom_up_package_dirs
read_package_contents = _WALK.read_package_contents


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


@dataclass(frozen=True)
class PackageFinding:
    package_dir: Path
    init_path: Path
    expected: list[str]
    actual: list[str]
    missing: list[str]
    extra: list[str]
    init_parse_error: bool = False
    all_eval_error: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_dir": self.package_dir.as_posix(),
            "init_path": self.init_path.as_posix(),
            "expected": list(self.expected),
            "actual": list(self.actual),
            "missing": list(self.missing),
            "extra": list(self.extra),
            "init_parse_error": bool(self.init_parse_error),
            "all_eval_error": bool(self.all_eval_error),
        }


def _init_path(package_dir: Path) -> Path:
    return package_dir / "__init__.py"


def _flatten_add_chain(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _flatten_add_chain(node.left) + _flatten_add_chain(node.right)
    return [node]


def _string_literals_from_sequence(node: ast.AST) -> list[str]:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    out: list[str] = []
    for elt in node.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            out.append(elt.value)
    return out


def _child_name_from_all_attr(node: ast.AST) -> str | None:
    """
    Recognize child `__all__` references:
      - child.__all__
      - list(child.__all__)
    Return child name if matched.
    """
    if isinstance(node, ast.Attribute) and node.attr == "__all__":
        if isinstance(node.value, ast.Name) and node.value.id:
            return node.value.id
        return None

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "list":
        if len(node.args) != 1:
            return None
        return _child_name_from_all_attr(node.args[0])

    return None


def _eval_all_expr(
    node: ast.AST, *, child_exports: dict[str, list[str]]
) -> tuple[list[str], bool]:
    """
    Evaluate a restricted `__all__ = ...` expression into a list of exported names.

    Supported:
    - list/tuple of string literals
    - list(child.__all__) or child.__all__
    - list literal with string literals
    - concatenation chain using + (binary add)
    """
    if isinstance(node, (ast.List, ast.Tuple)):
        return _string_literals_from_sequence(node), False

    child = _child_name_from_all_attr(node)
    if child is not None:
        return list(child_exports.get(child, [])), False

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        parts = _flatten_add_chain(node)
        out: list[str] = []
        any_err = False
        for part in parts:
            vals, err = _eval_all_expr(part, child_exports=child_exports)
            out.extend(vals)
            any_err = any_err or err
        return out, any_err

    return [], True


def _reexport_names_from_init_module(tree: ast.Module) -> list[str]:
    out: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (getattr(node, "level", 0) or 0) >= 1:
            for alias in getattr(node, "names", []):
                name = getattr(alias, "name", None)
                if isinstance(name, str) and name and name != "*":
                    asname = getattr(alias, "asname", None)
                    out.append(str(asname or name))
    return out


def _actual_exports_for_package(
    package_dir: Path, *, child_exports: dict[str, list[str]]
) -> tuple[list[str], bool, bool]:
    """
    Return (exports, init_parse_error, all_eval_error).

    Exports are derived from:
    - `__all__` (when statically evaluable under the supported expression subset)
    - relative re-exports: `from .x import Name` in `__init__.py`
    """
    init_py = _init_path(package_dir)
    if not init_py.exists():
        return [], False, False

    try:
        src = init_py.read_text(encoding="utf-8")
    except OSError:
        return [], True, True

    try:
        tree = ast.parse(src, filename=str(init_py))
    except SyntaxError:
        return [], True, True

    all_names: list[str] = []
    all_eval_error = False
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if isinstance(tgt, ast.Name) and tgt.id == "__all__":
            vals, err = _eval_all_expr(node.value, child_exports=child_exports)
            all_names = vals
            all_eval_error = err
            break

    exports = set(all_names) | set(_reexport_names_from_init_module(tree))
    return sorted(exports), False, bool(all_eval_error)


def _expected_exports_for_package(
    package_dir: Path, *, include_tests: bool, expected_by_dir: dict[Path, list[str]]
) -> list[str]:
    """
    Deterministic expected exports based on leaf-module public symbol extraction and
    child-package expected exports.
    """
    contents = read_package_contents(package_dir, include_tests=include_tests)

    module_exports: set[str] = set()
    for mod in contents.modules:
        syms = public_symbols_from_file(package_dir / f"{mod}.py")
        module_exports.update(syms)

    child_exports: set[str] = set()
    for child in contents.subpackages:
        child_dir = package_dir / child
        child_exports.update(expected_by_dir.get(child_dir.resolve(), []))

    return sorted(module_exports | child_exports)


def _compute_findings(root: Path, *, include_tests: bool) -> tuple[list[PackageFinding], int]:
    """
    Return (findings, init_parse_error_count).
    """
    root = root.resolve()
    pkgs = bottom_up_package_dirs(root, include_tests=include_tests)

    expected_by_dir: dict[Path, list[str]] = {}
    actual_by_dir: dict[Path, list[str]] = {}
    init_parse_error_count = 0

    findings: list[PackageFinding] = []

    for pkg_dir in pkgs:
        pkg_dir = pkg_dir.resolve()
        expected = _expected_exports_for_package(
            pkg_dir, include_tests=include_tests, expected_by_dir=expected_by_dir
        )
        expected_by_dir[pkg_dir] = expected

        child_exports = {}
        contents = read_package_contents(pkg_dir, include_tests=include_tests)
        for child in contents.subpackages:
            child_dir = (pkg_dir / child).resolve()
            child_exports[child] = actual_by_dir.get(child_dir, [])

        actual, init_parse_error, all_eval_error = _actual_exports_for_package(
            pkg_dir, child_exports=child_exports
        )
        actual_by_dir[pkg_dir] = actual

        if init_parse_error:
            init_parse_error_count += 1

        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))

        findings.append(
            PackageFinding(
                package_dir=pkg_dir,
                init_path=_init_path(pkg_dir),
                expected=expected,
                actual=actual,
                missing=missing,
                extra=extra,
                init_parse_error=init_parse_error,
                all_eval_error=all_eval_error,
            )
        )

    findings.sort(key=lambda f: str(f.package_dir))
    return findings, init_parse_error_count


def _write_artifacts(
    *,
    workspace: Path,
    output_dir: Path,
    generated: date,
    root: Path,
    include_tests: bool,
    findings: list[PackageFinding],
    init_parse_error_count: int,
    write_json: bool,
) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"public_symbol_export_check_{generated.isoformat()}.md"

    missing_pkgs = [f for f in findings if f.missing]
    missing_count = sum(len(f.missing) for f in findings)
    extra_count = sum(len(f.extra) for f in findings)
    all_eval_error_count = sum(1 for f in findings if f.all_eval_error)

    lines: list[str] = [
        "---",
        f"generated: {generated.isoformat()}",
        "artifact: public_symbol_export_check",
        "schema: public_symbol_export_check.v1",
        f"root: {root.resolve().as_posix()}",
        "---",
        "",
        "# Public symbol export check",
        "",
        f"- Root: `{root.resolve().as_posix()}`",
        f"- Include tests: {bool(include_tests)}",
        f"- Packages scanned: {len(findings)}",
        f"- Packages with missing exports: {len(missing_pkgs)}",
        f"- Missing exports (total): {missing_count}",
        f"- Extra exports vs generator (total): {extra_count}",
        f"- __init__.py parse errors: {int(init_parse_error_count)}",
        f"- __all__ eval warnings: {int(all_eval_error_count)}",
        "",
        "## How to fix",
        "",
        "- If the missing exports are intended to be public, run `regenerate_package_inits --fix` for the affected tree.",
        "- If the symbols are intentionally private, rename them with a leading underscore or refactor them out of leaf-module top-level scope.",
        "",
    ]

    if missing_count == 0:
        lines.append("✅ No missing exports detected.")
        lines.append("")
    else:
        lines.append("## Missing exports")
        lines.append("")
        for idx, f in enumerate(missing_pkgs, start=1):
            rel_pkg = f.package_dir.resolve().as_posix()
            lines.append(f"{idx}. `{rel_pkg}`")
            lines.append(f"   - Init: `{f.init_path.as_posix()}`")
            if f.init_parse_error:
                lines.append("   - ⚠️ Init parse error (unable to fully evaluate actual exports).")
            if f.all_eval_error:
                lines.append("   - ⚠️ __all__ expression not fully evaluable (restricted evaluator).")
            lines.append(f"   - Missing ({len(f.missing)}): `{', '.join(f.missing)}`")
        lines.append("")

    if extra_count > 0:
        lines.append("## Extra exports (vs deterministic generator)")
        lines.append("")
        for f in [x for x in findings if x.extra]:
            lines.append(f"- `{f.package_dir.as_posix()}`: `{', '.join(f.extra)}`")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out: dict[str, str | int] = {
        "md_path": str(md_path),
        "missing_count": int(missing_count),
        "extra_count": int(extra_count),
        "package_count": int(len(findings)),
        "init_parse_error_count": int(init_parse_error_count),
    }
    if write_json:
        payload = {
            "schema": "public_symbol_export_check.v1",
            "generated": generated.isoformat(),
            "workspace": workspace.as_posix(),
            "root": root.resolve().as_posix(),
            "include_tests": bool(include_tests),
            "package_count": int(len(findings)),
            "missing_count": int(missing_count),
            "extra_count": int(extra_count),
            "init_parse_error_count": int(init_parse_error_count),
            "findings": [f.to_dict() for f in findings],
        }
        json_path = output_dir / f"public_symbol_export_check_{generated.isoformat()}.json"
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
        help="Root directory to scan for packages (e.g. scripts/layers/layer_0_core).",
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
        help="Also write public_symbol_export_check_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include `tests/` directories and test_*.py modules (default: excluded).",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit with code 1 if missing_count exceeds --max-missing (default 0).",
    )
    parser.add_argument(
        "--max-missing",
        type=int,
        default=0,
        help="When using --fail-on-missing, allow up to this many missing exports (default: 0).",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit 1 if any package __init__.py failed to parse.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2

    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    findings, init_parse_error_count = _compute_findings(
        root, include_tests=bool(args.include_tests)
    )
    paths = _write_artifacts(
        workspace=workspace,
        output_dir=output_dir,
        generated=generated,
        root=root,
        include_tests=bool(args.include_tests),
        findings=findings,
        init_parse_error_count=init_parse_error_count,
        write_json=bool(args.json),
    )

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(
        "[SUMMARY] "
        f"packages={paths['package_count']} "
        f"missing={paths['missing_count']} "
        f"extra={paths['extra_count']} "
        f"init_parse_errors={paths['init_parse_error_count']}"
    )

    exit_code = 0
    if args.fail_on_missing:
        max_m = max(0, int(args.max_missing))
        mcount = int(paths.get("missing_count", 0))
        if mcount > max_m:
            print(
                f"❌ [FAIL] missing_count={mcount} exceeds --max-missing={max_m}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_parse_errors and int(paths.get("init_parse_error_count", 0)) > 0:
        print(
            f"❌ [FAIL] init_parse_error_count={paths.get('init_parse_error_count')}",
            file=sys.stderr,
        )
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

