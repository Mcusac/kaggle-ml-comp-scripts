"""Remove unused imports from sources using a check_health-style JSON report."""

from __future__ import annotations

import ast
import json
import io
import shutil
import subprocess
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.fix.text_span_rewrite_engine import (
    SpanEditOperation,
    apply_span_edit_operations,
)
from layers.layer_2_devtools.level_0_infra.level_0.formatting.import_organizer import (
    build_import_organizer_span_edit,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    module_to_file_path,
)


def load_health_report(path: Path) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-16") as f:
            content = f.read()
            json_start = content.find("{")
            if json_start > 0:
                content = content[json_start:]
            return json.loads(content)


@dataclass(frozen=True)
class _ImportStmt:
    start_line_idx0: int
    end_line_idx0_excl: int
    leading_text: str
    stmt_text: str


def _compute_prefix_end_line(lines: list[str]) -> int:
    # Keep consistent with import organizer behavior (shebang / encoding / docstring / future).
    idx = 0
    if idx < len(lines) and lines[idx].startswith("#!"):
        idx += 1

    # PEP 263 encoding cookie can be in first or second line (after shebang).
    for j in range(idx, min(len(lines), idx + 2)):
        if "coding" in lines[j]:
            idx = j + 1

    # Module docstring (token-based).
    src = "".join(lines[idx:])
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError:
        tokens = []
    for tok in tokens:
        if tok.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
            continue
        if tok.type == tokenize.STRING:
            idx = idx + tok.end[0]
        break

    # Consume blank lines and comments before future imports.
    while idx < len(lines) and (lines[idx].strip() == "" or lines[idx].lstrip().startswith("#")):
        idx += 1

    # Consume future imports (allow comments/blank lines between them).
    while True:
        progressed = False
        while idx < len(lines) and (lines[idx].strip() == "" or lines[idx].lstrip().startswith("#")):
            idx += 1
            progressed = True
        if idx < len(lines) and lines[idx].lstrip().startswith("from __future__ import "):
            idx += 1
            progressed = True
            continue
        if not progressed:
            break
    return idx


def _find_top_import_region_span(lines: list[str]) -> tuple[int, int] | None:
    """Return (start_line_idx0, end_line_idx0_excl) for the top import region."""
    prefix_end = _compute_prefix_end_line(lines)
    body = "".join(lines[prefix_end:])
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(body).readline))
    except tokenize.TokenError:
        return None

    def abs_line(rel_line_1: int) -> int:
        return prefix_end + (rel_line_1 - 1)

    start: int | None = None
    last_end: int | None = None
    paren = 0
    at_stmt_start = True
    saw_import = False
    in_import_stmt = False

    for tok in tokens:
        if tok.type == tokenize.ENDMARKER:
            break
        if tok.string in ("(", "[", "{"):
            paren += 1
        elif tok.string in (")", "]", "}"):
            paren = max(0, paren - 1)

        if tok.type in (tokenize.ENCODING, tokenize.NL, tokenize.COMMENT):
            continue
        if tok.type == tokenize.NEWLINE:
            if in_import_stmt and paren == 0:
                last_end = abs_line(tok.end[0]) + 1
                in_import_stmt = False
            at_stmt_start = True
            continue

        if tok.type in (tokenize.INDENT, tokenize.DEDENT):
            continue

        if paren == 0 and at_stmt_start:
            if tok.type == tokenize.NAME and tok.string in ("import", "from"):
                saw_import = True
                if start is None:
                    start = abs_line(tok.start[0])
                in_import_stmt = True
                at_stmt_start = False
                continue
            break

    if not saw_import or start is None or last_end is None:
        return None

    # Attach leading comment lines immediately above the first import (no blank line).
    s = start
    while s > 0:
        prev = lines[s - 1].strip()
        if prev == "":
            break
        if prev.startswith("#"):
            s -= 1
            continue
        break
    start = s

    # Extend end to include trailing blank/comment lines immediately after import block.
    end = last_end
    while end < len(lines):
        st = lines[end].strip()
        if st == "" or st.startswith("#"):
            end += 1
            continue
        break

    if start < 0 or end > len(lines) or start >= end:
        return None
    return start, end


def _extract_import_statements(region_lines: list[str]) -> list[_ImportStmt]:
    """Extract import statements, preserving leading attached comments."""
    region_text = "".join(region_lines)
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(region_text).readline))
    except tokenize.TokenError:
        return []

    stmts: list[_ImportStmt] = []
    stmt_start_line: int | None = None
    stmt_first_line_idx0: int | None = None
    paren = 0
    at_stmt_start = True
    for tok in tokens:
        if tok.type == tokenize.ENDMARKER:
            break
        if tok.string in ("(", "[", "{"):
            paren += 1
        elif tok.string in (")", "]", "}"):
            paren = max(0, paren - 1)
        if tok.type == tokenize.NL:
            continue
        if tok.type == tokenize.NEWLINE:
            if stmt_start_line is not None and paren == 0 and stmt_first_line_idx0 is not None:
                stmt_end_line_idx0_excl = tok.end[0]
                start_idx0 = stmt_start_line - 1
                end_idx0_excl = stmt_end_line_idx0_excl

                # Attach contiguous leading comment lines immediately above the statement (no blank line).
                lead_start = start_idx0
                i = start_idx0 - 1
                while i >= 0:
                    stripped = region_lines[i].strip()
                    if stripped == "":
                        break
                    if stripped.startswith("#"):
                        lead_start = i
                        i -= 1
                        continue
                    break

                leading_text = "".join(region_lines[lead_start:start_idx0])
                stmt_text = "".join(region_lines[start_idx0:end_idx0_excl])
                stmts.append(
                    _ImportStmt(
                        start_line_idx0=lead_start,
                        end_line_idx0_excl=end_idx0_excl,
                        leading_text=leading_text,
                        stmt_text=stmt_text,
                    )
                )
                stmt_start_line = None
                stmt_first_line_idx0 = None
            at_stmt_start = True
            continue
        if tok.type in (tokenize.ENCODING, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT):
            continue
        if at_stmt_start and paren == 0:
            if tok.type == tokenize.NAME and tok.string in ("import", "from"):
                stmt_start_line = tok.start[0]
                stmt_first_line_idx0 = tok.start[0] - 1
                at_stmt_start = False
                continue
            at_stmt_start = False
    return stmts


def _stmt_has_noqa(stmt_text: str) -> bool:
    lowered = stmt_text.lower()
    return "# noqa" in lowered or "#noqa" in lowered


def _strip_leading_comments(stmt_text: str) -> str:
    lines = stmt_text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        st = lines[i].lstrip()
        if st.startswith("#") or st.strip() == "":
            i += 1
            continue
        break
    return "".join(lines[i:])


def _render_import_stmt_after_removal(stmt_text: str, unused_names: set[str]) -> tuple[str, int] | None:
    """Return (new_stmt_text, removed_count) or None if no change."""
    if _stmt_has_noqa(stmt_text):
        return None
    core = _strip_leading_comments(stmt_text)
    if not core.strip():
        return None
    try:
        tree = ast.parse(core)
    except SyntaxError:
        return None
    if not tree.body:
        return None
    node = tree.body[0]

    if isinstance(node, ast.Import):
        kept: list[ast.alias] = []
        removed = 0
        for a in node.names:
            effective = a.asname or (a.name.split(".", 1)[0] if a.name else "")
            if effective in unused_names:
                removed += 1
            else:
                kept.append(a)
        if removed == 0:
            return None
        if not kept:
            return ("", removed)
        parts = []
        for a in kept:
            if a.asname:
                parts.append(f"{a.name} as {a.asname}")
            else:
                parts.append(a.name)
        return (f"import {', '.join(parts)}\n", removed)

    if isinstance(node, ast.ImportFrom):
        if node.names and any(a.name == "*" for a in node.names):
            return None
        kept2: list[ast.alias] = []
        removed2 = 0
        for a in node.names:
            effective = a.asname or a.name
            if effective in unused_names:
                removed2 += 1
            else:
                kept2.append(a)
        if removed2 == 0:
            return None
        if not kept2:
            return ("", removed2)
        module_prefix = "." * int(node.level or 0)
        mod = node.module or ""
        from_mod = f"{module_prefix}{mod}".rstrip(".")
        if not from_mod:
            from_mod = module_prefix or mod
        parts2 = []
        for a in kept2:
            if a.asname:
                parts2.append(f"{a.name} as {a.asname}")
            else:
                parts2.append(a.name)
        return (f"from {from_mod} import {', '.join(parts2)}\n", removed2)

    return None


def _build_unused_import_cleanup_span_edit(
    *,
    path: Path,
    unused_names: set[str],
) -> tuple[SpanEditOperation | None, int, list[str]]:
    """Build a drift-safe span edit for the top-of-file import region only."""
    warnings: list[str] = []
    try:
        raw = path.read_bytes().decode("utf-8")
    except OSError as exc:
        return None, 0, [str(exc)]

    normalized = raw.replace("\r\n", "\n")
    lines = normalized.splitlines(keepends=True)
    span = _find_top_import_region_span(lines)
    if span is None:
        return None, 0, []
    start_line_idx0, end_line_idx0_excl = span
    if start_line_idx0 >= end_line_idx0_excl:
        return None, 0, []

    region_lines = list(lines[start_line_idx0:end_line_idx0_excl])
    old_region = "".join(region_lines)
    stmts = _extract_import_statements(region_lines)
    if not stmts:
        return None, 0, []

    removed_total = 0
    out_lines: list[str] = []
    cursor = 0
    for st in stmts:
        # Keep non-statement content between previous cursor and this stmt start.
        if st.start_line_idx0 > cursor:
            out_lines.append("".join(region_lines[cursor:st.start_line_idx0]))

        rendered = _render_import_stmt_after_removal(st.stmt_text, unused_names)
        if rendered is None:
            out_lines.append("".join(region_lines[st.start_line_idx0:st.end_line_idx0_excl]))
        else:
            new_stmt, removed = rendered
            removed_total += removed
            # Preserve attached leading comments and drop statement when empty.
            if new_stmt:
                out_lines.append(st.leading_text)
                out_lines.append(new_stmt)
        cursor = st.end_line_idx0_excl

    if cursor < len(region_lines):
        out_lines.append("".join(region_lines[cursor:]))

    new_region = "".join(out_lines)
    if new_region == old_region:
        return None, 0, warnings

    return (
        SpanEditOperation(
            path=path,
            start_line=start_line_idx0 + 1,
            end_line_excl=end_line_idx0_excl + 1,
            kind="UNUSED_IMPORT_CLEANUP",
            old_text=old_region,
            new_text=new_region,
        ),
        removed_total,
        warnings,
    )


class UnusedImportRemover:
    """Remove unused imports from Python files."""

    def __init__(self, root: Path, dry_run: bool = False, *, organize_imports: bool = True):
        self.root = root
        self.dry_run = dry_run
        self.organize_imports = organize_imports
        self.stats = {
            "files_considered": 0,
            "files_changed": 0,
            "imports_removed": 0,
            "edits_applied": 0,
            "drift_failures": 0,
            "modules_missing": 0,
            "warnings": 0,
        }
        self.changed_files: list[Path] = []

    def process_report(self, report_data: dict[str, Any]) -> None:
        unused_imports = report_data.get("dead_code", {}).get("unused_imports", [])

        print(f"📋 Processing {len(unused_imports)} modules with unused imports...")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        print()

        for module_info in unused_imports:
            self._process_module(module_info)

        self._print_summary()

    def _process_module(self, module_info: dict[str, Any]) -> None:
        module = module_info.get("module")
        names = module_info.get("names")
        if not isinstance(module, str) or not isinstance(names, list):
            return
        unused_names = {n for n in names if isinstance(n, str) and n}

        file_path = module_to_file_path(root=self.root, module=module)
        if file_path is None:
            self.stats["modules_missing"] += 1
            print(f"⚠️  {module}: File not found under root={self.root}")
            return

        self.stats["files_considered"] += 1
        op, removed_count, warnings = _build_unused_import_cleanup_span_edit(
            path=file_path,
            unused_names=unused_names,
        )
        if warnings:
            self.stats["warnings"] += len(warnings)
        if op is None or removed_count <= 0:
            return

        print(f"{'🔍' if self.dry_run else '✅'} {module}")
        preview = ", ".join(sorted(unused_names)[:5])
        if preview:
            print(f"   Planned removals: {preview}")
            if len(unused_names) > 5:
                print(f"   ... and {len(unused_names) - 5} more")

        results, summary, errors = apply_span_edit_operations(
            [op],
            apply=not self.dry_run,
            max_changes_per_file=10,
        )
        applied = any(r.applied for r in results)
        if errors:
            # Drift failures surface as errors.
            self.stats["drift_failures"] += len(errors)
            for e in errors[:3]:
                print(f"⚠️  {e}")
            if len(errors) > 3:
                print(f"⚠️  ... and {len(errors) - 3} more errors")

        if applied:
            self.stats["files_changed"] += int(summary.files_changed)
            self.stats["edits_applied"] += int(summary.edits_applied)
            self.stats["imports_removed"] += int(removed_count)
            self.changed_files.append(file_path)

        if applied and self.organize_imports and not self.dry_run:
            org = build_import_organizer_span_edit(file_path)
            if org.op is not None:
                org_results, org_summary, org_errors = apply_span_edit_operations(
                    [org.op],
                    apply=True,
                    max_changes_per_file=10,
                )
                if any(r.applied for r in org_results):
                    self.stats["files_changed"] += int(org_summary.files_changed)
                    self.stats["edits_applied"] += int(org_summary.edits_applied)
                    if file_path not in self.changed_files:
                        self.changed_files.append(file_path)
                if org_errors:
                    self.stats["drift_failures"] += len(org_errors)
                    for e in org_errors[:3]:
                        print(f"⚠️  {e}")
                    if len(org_errors) > 3:
                        print(f"⚠️  ... and {len(org_errors) - 3} more errors")

    def _print_summary(self) -> None:
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Files considered: {self.stats['files_considered']}")
        print(f"Files changed: {self.stats['files_changed']}")
        print(f"Imports removed: {self.stats['imports_removed']}")
        print(f"Edits applied: {self.stats['edits_applied']}")
        print(f"Missing modules: {self.stats['modules_missing']}")
        print(f"Drift failures: {self.stats['drift_failures']}")
        if self.dry_run:
            print("\n[DRY RUN] No files were actually modified.")


def _run_external_formatter(
    *,
    tool: str,
    files: list[Path],
    extra_args: list[str] | None,
) -> int:
    if not files:
        return 0
    exe = shutil.which(tool)
    if not exe:
        print(f"⚠️  Formatter not found on PATH: {tool}")
        return 0

    args = list(extra_args or [])
    file_args = [str(p) for p in files]

    if tool == "ruff":
        cmd = [exe, "format", *args, *file_args]
    elif tool == "black":
        cmd = [exe, *args, *file_args]
    else:
        print(f"⚠️  Unsupported formatter tool: {tool}")
        return 0

    try:
        proc = subprocess.run(cmd, check=False)
        if proc.returncode != 0:
            print(f"⚠️  Formatter exited non-zero: {tool} (code={proc.returncode})")
        return int(proc.returncode)
    except OSError as exc:
        print(f"⚠️  Failed to run formatter {tool}: {exc}")
        return 1


def run_unused_import_cleanup(
    *,
    report: Path,
    root: Path,
    dry_run: bool,
    organize_imports: bool = True,
    format_after: bool = False,
    format_tool: str = "ruff",
    format_args: list[str] | None = None,
) -> int:
    if not report.is_file():
        print(f"❌ Error: Report file not found: {report}")
        return 1
    data = load_health_report(report)
    remover = UnusedImportRemover(root, dry_run=dry_run, organize_imports=organize_imports)
    remover.process_report(data)
    if format_after and not dry_run:
        return _run_external_formatter(
            tool=format_tool,
            files=sorted(set(remover.changed_files), key=lambda p: p.as_posix()),
            extra_args=format_args,
        )
    return 0
