"""
Codemod: rename module-level ``logger = get_logger(__name__)`` and
``torch = get_torch()`` to ``_logger`` / ``_torch`` and update all ``ast.Name``
uses of those names in the same file.

**Skip** a file if ``logger`` / ``torch`` is also bound in a nested scope, bound
at module level via a conflicting import, target names (``_logger`` /
``_torch``) are already used, or a ``*`` import appears at module level.

**Run** (default root: ``kaggle-ml-comp-scripts/scripts/``)::

  cd kaggle-ml-comp-scripts/scripts
  python -m layers.layer_2_devtools.level_1_impl.level_0.privatize_logger_torch_globals
  python -m layers.layer_2_devtools.level_1_impl.level_0.privatize_logger_torch_globals --dry-run
  python -m layers.layer_2_devtools.level_1_impl.level_0.privatize_logger_torch_globals --verbose

**After apply:** refresh deterministic ``__init__.py`` barrels (then ``--check``)::

  cd kaggle-ml-comp-scripts/scripts
  python layers/layer_2_devtools/level_1_impl/level_2/regenerate_package_inits.py --root layers --fix
  python layers/layer_2_devtools/level_1_impl/level_2/regenerate_package_inits.py --root layers --check

If import errors occur during ``--check`` (optional deps / heavy imports from
``layers``), use a venv with ``requirements.txt`` installed, or call
``check_regeneration`` from ``regenerate_inits.apply`` in isolation.

**Optional** static re-scan: ``python -m layers.layer_2_devtools.level_1_impl.level_2.scan_level_violations --json``
(see ``kaggle-ml-scripts.mdc``).
"""

from __future__ import annotations

import ast
import difflib
import io
import sys
import tokenize
from argparse import ArgumentParser
from io import StringIO
from pathlib import Path
from typing import Sequence

# `privatize_logger_torch_globals.py` is in `.../level_0/`; parents[4] is `.../scripts/`
_SCRIPTS = Path(__file__).resolve().parents[4]
_DEFAULT_ROOT = _SCRIPTS


def _is_get_logger_name_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if not isinstance(node.func, ast.Name) or node.func.id != "get_logger":
        return False
    if len(node.args) != 1 or node.keywords:
        return False
    a0 = node.args[0]
    return isinstance(a0, ast.Name) and a0.id == "__name__"


def _is_get_torch_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if not isinstance(node.func, ast.Name) or node.func.id != "get_torch":
        return False
    return not node.args and not node.keywords


def _module_level_targets(tree: ast.Module) -> tuple[bool, bool]:
    has_logger = False
    has_torch = False
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        t = node.targets[0]
        if not isinstance(t, ast.Name):
            continue
        if t.id == "logger" and _is_get_logger_name_call(node.value):
            has_logger = True
        if t.id == "torch" and _is_get_torch_call(node.value):
            has_torch = True
    return has_logger, has_torch


def _import_local_name(alias: ast.alias) -> str:
    if alias.name == "*":
        return "*"
    if alias.asname:
        return alias.asname
    return alias.name.split(".", 1)[0]


def _module_has_star_import(tree: ast.Module) -> bool:
    for n in tree.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "*":
                    return True
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name == "*":
                    return True
    return False


def _module_binds_name_via_import(tree: ast.Module, name: str) -> bool:
    for n in tree.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "*":
                    return True
                if _import_local_name(a) == name:
                    return True
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name == "*":
                    return True
                if _import_local_name(a) == name:
                    return True
    return False


def _add_bind_target(t: ast.AST, out: set[str]) -> None:
    if isinstance(t, ast.Name) and t.id in ("logger", "torch"):
        out.add(t.id)
    elif isinstance(t, (ast.Tuple, ast.List)):
        for el in t.elts:
            _add_bind_target(el, out)


def _param_names(args: ast.arguments) -> set[str]:
    out: set[str] = set()
    for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
        out.add(a.arg)
    if args.vararg is not None and isinstance(args.vararg, ast.arg):
        out.add(args.vararg.arg)
    if args.kwarg is not None and isinstance(args.kwarg, ast.arg):
        out.add(args.kwarg.arg)
    return out


class _ShadowFinder(ast.NodeVisitor):
    """
    If ``logger`` or ``torch`` is **bound** in any scope that is not the module
    body (incl. class body, function body, except targets, for/comp targets, etc.),
    record the name. Does **not** treat module-level `logger`/`torch` = ... as
    shadowing (we only descend into non-module child scopes from visit_Module).
    """

    def __init__(self) -> None:
        self.bad: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for a in node.names:
            if _import_local_name(a) in ("logger", "torch"):
                self.bad.add(_import_local_name(a))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for a in node.names:
            if a.name == "*":
                self.bad.add("logger")
                self.bad.add("torch")
            elif _import_local_name(a) in ("logger", "torch"):
                self.bad.add(_import_local_name(a))
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        if isinstance(node.target, ast.Name) and node.target.id in (
            "logger",
            "torch",
        ):
            self.bad.add(node.target.id)
        self.visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        _add_bind_target(node.target, self.bad)
        if node.value is not None:
            self.visit(node.value)
        self.visit(node.annotation)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name) and node.target.id in ("logger", "torch"):
            self.bad.add(node.target.id)
        self.visit(node.value)

    def visit_Assign(self, node: ast.Assign) -> None:
        for t in node.targets:
            _add_bind_target(t, self.bad)
        self.visit(node.value)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None and node.name in ("logger", "torch"):
            self.bad.add(node.name)
        if node.type is not None:
            self.visit(node.type)
        for b in node.body:
            self.visit(b)

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        for c in node.cases:
            self.visit(c)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None and node.name in ("logger", "torch"):
            self.bad.add(node.name)
        if node.pattern is not None:
            self.visit(node.pattern)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        for r in (node.keys or []):
            self.visit(r)
        for p in (node.patterns or []):
            self.visit(p)
        rest = getattr(node, "rest", None)
        if rest is not None and isinstance(rest, str) and rest in ("logger", "torch"):
            self.bad.add(rest)
        for v in (node.values or []):
            self.visit(v)

    def visit_MatchClass(self, node: ast.MatchClass) -> None:
        for p in node.patterns or []:
            self.visit(p)
        for p in (node.kwd_patterns or []):
            self.visit(p)

    def visit_For(self, node: ast.For) -> None:
        _add_bind_target(node.target, self.bad)
        self.visit(node.iter)
        for b in node.body + node.orelse:
            self.visit(b)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        return self.visit_For(node)  # type: ignore[return]

    def visit_comp(self, node: ast.AST) -> None:
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            for gen in node.generators:
                _add_bind_target(gen.target, self.bad)
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self.visit_comp(node)
        for gen in node.generators:
            self.visit(gen.iter)
            for e in gen.ifs:
                self.visit(e)
        self.visit(node.elt)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self.visit_comp(node)
        for gen in node.generators:
            self.visit(gen.iter)
            for e in gen.ifs:
                self.visit(e)
        self.visit(node.elt)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self.visit_comp(node)
        for gen in node.generators:
            self.visit(gen.iter)
            for e in gen.ifs:
                self.visit(e)
        self.visit(node.elt)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self.visit_comp(node)
        for gen in node.generators:
            self.visit(gen.iter)
            for e in gen.ifs:
                self.visit(e)
        self.visit(node.key)
        self.visit(node.value)

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if item.optional_vars is not None:
                v = item.optional_vars
                if isinstance(v, ast.Name) and v.id in ("logger", "torch"):
                    self.bad.add(v.id)
                else:
                    _add_bind_target(v, self.bad)
            self.visit(item.context_expr)
        for b in node.body:
            self.visit(b)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        for item in node.items:
            if item.optional_vars is not None:
                v = item.optional_vars
                if isinstance(v, ast.Name) and v.id in ("logger", "torch"):
                    self.bad.add(v.id)
                else:
                    _add_bind_target(v, self.bad)
            self.visit(item.context_expr)
        for b in node.body:
            self.visit(b)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for p in _param_names(node.args):
            if p in ("logger", "torch"):
                self.bad.add(p)
        self.visit(node.body)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for b in node.bases + node.keywords:
            self.visit(b)
        for d in node.decorator_list:
            self.visit(d)
        for m in node.body:
            self.visit(m)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for p in _param_names(node.args):
            if p in ("logger", "torch"):
                self.bad.add(p)
        for d in node.decorator_list:
            self.visit(d)
        for t in (node.returns,):
            if t is not None:
                self.visit(t)
        for s in node.body:
            self.visit(s)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        for p in _param_names(node.args):
            if p in ("logger", "torch"):
                self.bad.add(p)
        for d in node.decorator_list:
            self.visit(d)
        for t in (node.returns,):
            if t is not None:
                self.visit(t)
        for s in node.body:
            self.visit(s)

    def visit_Global(self, node: ast.Global) -> None:
        for n in node.names:
            if n in ("logger", "torch"):
                self.bad.add(n)
        self.generic_visit(node)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        for n in node.names:
            if n in ("logger", "torch"):
                self.bad.add(n)
        self.generic_visit(node)


def _nested_binds_logger_or_torch(tree: ast.Module) -> set[str]:
    sf = _ShadowFinder()
    for n in tree.body:
        if isinstance(
            n,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            sf.visit(n)
        if isinstance(
            n,
            (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp, ast.Lambda),
        ):
            sf.visit(n)
    return sf.bad


def _name_has_end(node: ast.Name) -> bool:
    e = getattr(node, "end_col_offset", None)
    el = getattr(node, "end_lineno", None)
    return e is not None and el is not None


def _collect_name_replacement_spans(
    tree: ast.AST,
    renames: dict[str, str],
) -> list[tuple[int, int, int, int, str, str]] | None:
    out: list[tuple[int, int, int, int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or node.id not in renames:
            continue
        if not _name_has_end(node) or not hasattr(node, "col_offset") or node.col_offset is None:
            return None
        if node.lineno is None:  # pragma: no cover
            return None
        new_id = renames[node.id]
        en = node.end_lineno
        ec = node.end_col_offset
        if not isinstance(en, int) or not isinstance(ec, int):  # pragma: no cover
            return None
        out.append(
            (
                node.lineno,
                node.col_offset,
                en,
                ec,
                node.id,
                new_id,
            )
        )
    return out


def _apply_renames_in_source(
    source: str,
    renames: dict[str, str],
    tree: ast.AST,
) -> tuple[str | None, str]:
    spans = _collect_name_replacement_spans(tree, renames)
    if spans is None:
        return None, "incomplete_name_positions_in_ast"
    if not spans:
        return source, "no_renames"
    new_vals = set(renames.values())
    for st_ln, st_col, end_ln, end_col, _old, new in spans:
        if st_ln != end_ln:
            return None, "name_spans_multiline"
        if new not in new_vals:
            return None, "internal_error"
    fixed: list[tuple[int, int, int, int, str, str]] = list(spans)
    out_lines = source.splitlines(keepends=True)
    fixed.sort(key=lambda r: (r[2], r[3], r[0], r[1]), reverse=True)
    for st_ln, st_col, end_ln, end_col, old_id, new_id in fixed:
        li = st_ln - 1
        line = out_lines[li]
        if not line:
            return None, "empty_line"
        chunk = line[st_col:end_col]
        if chunk != old_id:
            return None, f"expected {old_id!r} at L{st_ln} col {st_col} got {chunk!r}"
        out_lines[li] = line[:st_col] + new_id + line[end_col:]
    return "".join(out_lines), "ok"


def _validate_token_roundtrip(source: str) -> str | None:
    """Return error string if source does not round-trip tokenize."""
    try:
        list(tokenize.generate_tokens(StringIO(source).readline))
    except tokenize.TokenError as e:  # pragma: no cover
        return str(e)
    return None


def _name_already_used_in_ast(tree: ast.AST, name: str) -> bool:
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id == name:
            return True
    return False


def _process_file(
    path: Path,
    *,
    dry_run: bool,
) -> tuple[str, str | None, str | None]:
    try:
        src0 = path.read_text(encoding="utf-8")
    except OSError as e:  # pragma: no cover
        return "error", str(e), None
    if "\x00" in src0:  # pragma: no cover
        return "skip", "null_byte", None
    try:
        tree0 = ast.parse(src0, filename=str(path))
    except SyntaxError as e:
        return "skip", f"syntax: {e}", None
    if not isinstance(tree0, ast.Module):
        return "skip", "not_module", None
    h_log, h_torch = _module_level_targets(tree0)
    if not h_log and not h_torch:
        return "skip", "no_targets", None
    renames: dict[str, str] = {}
    if h_log:
        renames["logger"] = "_logger"
    if h_torch:
        renames["torch"] = "_torch"
    for old, new in renames.items():
        if _name_already_used_in_ast(tree0, new):
            return "skip", f"target {new!r} already in use", None
    if h_log and _module_binds_name_via_import(tree0, "logger"):
        return "skip", "import binds logger", None
    if h_torch and _module_binds_name_via_import(tree0, "torch"):
        return "skip", "import binds torch", None
    if _module_has_star_import(tree0):
        return "skip", "star_import", None
    bad = _nested_binds_logger_or_torch(tree0)
    relevant = bad & set(renames)
    if relevant:
        return "skip", f"nested_bind:{sorted(relevant)}", None
    new_src, st = _apply_renames_in_source(src0, renames, tree0)
    if not new_src or st != "ok":
        return "skip", st or "apply_failed", None
    to_err = _validate_token_roundtrip(new_src)
    if to_err:
        return "skip", f"tokenize_after: {to_err}", None
    try:
        ast.parse(new_src, filename=str(path))
    except SyntaxError as e:
        return "skip", f"parse_after: {e}", None
    if new_src == src0:
        return "skip", "no_change", None
    if dry_run:
        return "ok_dry", None, _unified_diff(path, src0, new_src)
    try:
        path.write_text(new_src, encoding="utf-8")
    except OSError as e:  # pragma: no cover
        return "error", f"write: {e}", None
    return "ok", None, _unified_diff(path, src0, new_src)


def _unified_diff(path: Path, before: str, after: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"{path} (before)",
            tofile=f"{path} (after)",
            lineterm="",
        )
    )


def _iter_py_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(root.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        out.append(p)
    return out


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )


def main(argv: Sequence[str] | None = None) -> int:
    _win_utf8_stdio()
    p = ArgumentParser(
        description="Privatize module-level get_logger / get_torch bindings "
        "and rename uses to _logger / _torch."
    )
    p.add_argument(
        "--root",
        type=Path,
        default=_DEFAULT_ROOT,
        help="Root directory to search for *.py (default: .../kaggle-ml-comp-scripts/scripts).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; print summary and per-file diffs for changed files.",
    )
    p.add_argument(
        "--print-skips",
        action="store_true",
        help="Log skip reasons (per file) to stdout.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Per file: show unified diffs (large). Default: one line per change (dry_run) or summary only (apply).",
    )
    args = p.parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 1
    results: list[tuple[Path, str, str | None, str | None]] = []
    for path in _iter_py_files(root):
        status, reason, diff = _process_file(path, dry_run=bool(args.dry_run))
        results.append((path, status, reason, diff))
    ok = sum(1 for _p, s, _r, _d in results if s in ("ok", "ok_dry"))
    skipped = sum(1 for _p, s, _r, _d in results if s == "skip")
    errs = sum(1 for _p, s, _r, _d in results if s == "error")
    for path, status, reason, diff in results:
        if status == "skip" and args.print_skips and reason and reason not in (
            "no_targets",
        ):
            print(f"SKIP {path}: {reason}")
        if status in ("ok", "ok_dry") and diff:
            prefix = "WOULD UPDATE " if status == "ok_dry" else "UPDATED "
            if args.verbose:
                print(f"{prefix}{path}")
                print(diff, end="")
                print()
            elif args.dry_run:
                print(f"{prefix}{path}")
    print(
        f"Done: {ok} updated"
        f"{' (dry_run)' if args.dry_run else ''}, "
        f"{skipped} skipped, {errs} errors."
    )
    if errs:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
