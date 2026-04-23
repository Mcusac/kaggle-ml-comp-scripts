from __future__ import annotations

import io
import re
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from layers.layer_2_devtools.level_0_infra.level_0.fix.text_span_rewrite_engine import (
    SpanEditOperation,
)


_ENCODING_COOKIE_RE = re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)")
_LEVEL_RE = re.compile(r"^level_(\d+)$")

_GROUP_PREFIX_COMPETITION_INFRA = "layers.layer_1_competition.level_0_infra"
_GROUP_PREFIX_CONTESTS = "layers.layer_1_competition.contests"


@dataclass(frozen=True)
class ImportOrganizerItem:
    group: int
    module_sort_key: tuple[object, ...]
    statement_sort_key: str
    text: str


@dataclass(frozen=True)
class ImportOrganizerResult:
    changed: bool
    new_text: str
    warnings: list[str]


@dataclass(frozen=True)
class ImportOrganizerSpanResult:
    """Result for producing a safe span edit on an existing file."""

    op: SpanEditOperation | None
    warnings: list[str]


def organize_imports_text(text: str) -> ImportOrganizerResult:
    """Rewrite top-of-file import region to match `python-import-order.mdc` grouping.

    Conservative rules:
    - Only rewrites a contiguous top-of-file import region (after shebang/encoding/docstring/future).
    - Skips rewrite when parsing is ambiguous or when no import region exists.
    """
    newline = "\r\n" if "\r\n" in text else "\n"
    normalized = text.replace("\r\n", "\n")
    lines = normalized.splitlines(keepends=True)

    span = _find_top_import_region_span(lines)
    if span is None:
        return ImportOrganizerResult(changed=False, new_text=text, warnings=[])
    start_line, end_line = span
    if start_line >= end_line:
        return ImportOrganizerResult(changed=False, new_text=text, warnings=[])

    region_text = "".join(lines[start_line:end_line])
    items, warnings = _extract_import_items(region_text, region_start_line=start_line)
    if warnings:
        return ImportOrganizerResult(changed=False, new_text=text, warnings=warnings)
    if not items:
        return ImportOrganizerResult(changed=False, new_text=text, warnings=[])

    rewritten_region = _render_grouped_items(items)
    if rewritten_region == region_text:
        return ImportOrganizerResult(changed=False, new_text=text, warnings=[])

    new_lines = list(lines)
    new_lines[start_line:end_line] = [rewritten_region]
    out = "".join(new_lines)
    if newline == "\r\n":
        out = out.replace("\n", "\r\n")
    return ImportOrganizerResult(changed=True, new_text=out, warnings=[])


def build_import_organizer_span_edit(path: Path) -> ImportOrganizerSpanResult:
    """Build a safe `SpanEditOperation` to organize imports for a single file."""
    try:
        raw = path.read_bytes().decode("utf-8")
    except OSError as exc:
        return ImportOrganizerSpanResult(op=None, warnings=[str(exc)])

    normalized = raw.replace("\r\n", "\n")
    lines = normalized.splitlines(keepends=True)
    span = _find_top_import_region_span(lines)
    if span is None:
        return ImportOrganizerSpanResult(op=None, warnings=[])
    start_line, end_line = span
    if start_line >= end_line:
        return ImportOrganizerSpanResult(op=None, warnings=[])

    old_region = "".join(lines[start_line:end_line])
    items, warnings = _extract_import_items(old_region, region_start_line=start_line)
    if warnings:
        return ImportOrganizerSpanResult(op=None, warnings=warnings)
    if not items:
        return ImportOrganizerSpanResult(op=None, warnings=[])

    new_region = _render_grouped_items(items)
    if new_region == old_region:
        return ImportOrganizerSpanResult(op=None, warnings=[])

    return ImportOrganizerSpanResult(
        op=SpanEditOperation(
            path=path,
            start_line=start_line + 1,
            end_line_excl=end_line + 1,
            kind="IMPORT_ORGANIZE",
            old_text=old_region,
            new_text=new_region,
        ),
        warnings=[],
    )


def _find_top_import_region_span(lines: Sequence[str]) -> tuple[int, int] | None:
    """Return (start_line_idx, end_line_idx_exclusive) for the import region.

    The region starts at the first import statement after:
    - optional shebang/encoding cookie
    - optional module docstring
    - optional `from __future__ import ...` block
    and ends after the last contiguous top import statement (including intervening blanks/comments).
    """
    prefix_end = _compute_prefix_end_line(lines)
    body = "".join(lines[prefix_end:])

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(body).readline))
    except tokenize.TokenError:
        return None

    # Map prefix-relative line numbers back to absolute line indices.
    def abs_line(rel_line_1: int) -> int:
        return prefix_end + (rel_line_1 - 1)

    start: int | None = None
    last_end: int | None = None
    paren = 0
    at_stmt_start = True
    saw_import = False

    for tok in tokens:
        if tok.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
            if tok.type == tokenize.NEWLINE:
                at_stmt_start = True
            continue
        if tok.type == tokenize.ENDMARKER:
            break

        if tok.string in ("(", "[", "{"):
            paren += 1
        elif tok.string in (")", "]", "}"):
            paren = max(0, paren - 1)

        # Only consider top-level statements (paren==0) for boundaries.
        if not at_stmt_start or paren != 0:
            continue

        # Skip leading INDENT/DEDENT defensively; top-of-file should not have them.
        if tok.type in (tokenize.INDENT, tokenize.DEDENT):
            continue

        if tok.type == tokenize.NAME and tok.string in ("import", "from"):
            saw_import = True
            if start is None:
                start = abs_line(tok.start[0])
            # We'll update end when we later see NEWLINE at paren==0 for this statement.
            at_stmt_start = False
            continue

        # First non-import statement ends the import region.
        break

    if not saw_import or start is None:
        return None

    # Expand start upward to include contiguous leading comment lines immediately
    # attached to the first import statement (no blank lines between).
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

    # Now find the end: include all lines until after the last import statement,
    # including blank/comment lines between import statements. We scan again but
    # this time track statement NEWLINE boundaries for import statements.
    paren = 0
    at_stmt_start = True
    in_import_stmt = False
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
            if in_import_stmt and paren == 0:
                last_end = abs_line(tok.end[0]) + 1
                in_import_stmt = False
            at_stmt_start = True
            continue
        if tok.type == tokenize.COMMENT:
            continue
        if tok.type == tokenize.ENCODING:
            continue

        if paren == 0 and at_stmt_start:
            if tok.type == tokenize.NAME and tok.string in ("import", "from"):
                in_import_stmt = True
                at_stmt_start = False
                continue
            # Non-import statement; stop.
            break

    if last_end is None:
        return None

    # Extend end to include immediately following blank/comment lines, but stop
    # at first non-blank/non-comment line.
    end = last_end
    while end < len(lines):
        s = lines[end].strip()
        if s == "" or s.startswith("#"):
            end += 1
            continue
        break

    if start < 0 or end > len(lines) or start >= end:
        return None
    return start, end


def _compute_prefix_end_line(lines: Sequence[str]) -> int:
    """Return the first line index after shebang/encoding/docstring/future block."""
    idx = 0
    if idx < len(lines) and lines[idx].startswith("#!"):
        idx += 1

    # PEP 263 encoding cookie can be in first or second line (after shebang).
    for j in range(idx, min(len(lines), idx + 2)):
        if _ENCODING_COOKIE_RE.match(lines[j]):
            idx = j + 1

    doc_end = _module_docstring_end_line(lines, start_idx=idx)
    if doc_end is not None:
        idx = doc_end

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


def _module_docstring_end_line(lines: Sequence[str], *, start_idx: int) -> int | None:
    """Return the first line index after the module docstring, else None.

    Uses tokenization to avoid false positives from strings later in the file.
    """
    src = "".join(lines[start_idx:])
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError:
        return None

    for tok in tokens:
        if tok.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
            continue
        if tok.type == tokenize.STRING:
            # First real token is a string => module docstring.
            end_rel = tok.end[0]
            return start_idx + end_rel
        break
    return None


def _extract_import_items(
    region_text: str, *, region_start_line: int
) -> tuple[list[ImportOrganizerItem], list[str]]:
    """Split an import region into items (statement + attached leading comments)."""
    warnings: list[str] = []
    region_lines = region_text.splitlines(keepends=True)
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(region_text).readline))
    except tokenize.TokenError as exc:
        return [], [f"tokenize error in import region at line {region_start_line + 1}: {exc}"]

    items: list[ImportOrganizerItem] = []
    stmt_start_line: int | None = None
    stmt_end_line: int | None = None
    stmt_first_tok: tokenize.TokenInfo | None = None
    paren = 0
    at_stmt_start = True

    for tok in tokens:
        if tok.string in ("(", "[", "{"):
            paren += 1
        elif tok.string in (")", "]", "}"):
            paren = max(0, paren - 1)

        if tok.type == tokenize.ENDMARKER:
            break

        if tok.type == tokenize.NL:
            continue

        if tok.type == tokenize.NEWLINE:
            if stmt_start_line is not None and paren == 0:
                stmt_end_line = tok.end[0]
                if stmt_first_tok is None:
                    warnings.append("internal parse error: missing statement head token")
                    return [], warnings
                item = _build_item_from_statement(
                    region_lines,
                    stmt_start_line=stmt_start_line,
                    stmt_end_line=stmt_end_line,
                    stmt_first_tok=stmt_first_tok,
                )
                if item is None:
                    warnings.append(
                        f"unsupported or ambiguous import statement starting at line {region_start_line + stmt_start_line}"
                    )
                    return [], warnings
                items.append(item)
                stmt_start_line = None
                stmt_end_line = None
                stmt_first_tok = None
            at_stmt_start = True
            continue

        if tok.type in (tokenize.ENCODING, tokenize.COMMENT):
            continue
        if tok.type in (tokenize.INDENT, tokenize.DEDENT):
            continue

        if at_stmt_start and paren == 0:
            # Find first token of a statement; we only accept import/from.
            if tok.type == tokenize.NAME and tok.string in ("import", "from"):
                stmt_start_line = tok.start[0]
                stmt_first_tok = tok
                at_stmt_start = False
                continue
            # Non-import token inside region: region extraction should have prevented this.
            warnings.append(
                f"non-import statement encountered in import region at line {region_start_line + tok.start[0]}"
            )
            return [], warnings

    # Sort within groups deterministically.
    items_sorted = sorted(items, key=lambda it: (it.group, it.module_sort_key, it.statement_sort_key))
    return items_sorted, []


def _build_item_from_statement(
    region_lines: Sequence[str],
    *,
    stmt_start_line: int,
    stmt_end_line: int,
    stmt_first_tok: tokenize.TokenInfo,
) -> ImportOrganizerItem | None:
    start_idx0 = stmt_start_line - 1
    end_idx0_excl = stmt_end_line

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

    text = "".join(region_lines[lead_start:end_idx0_excl])
    group = _classify_group(stmt_first_tok, text=text)
    module_key = _module_sort_key(stmt_first_tok, text=text)
    stmt_key = _statement_sort_key(text)
    return ImportOrganizerItem(
        group=group,
        module_sort_key=module_key,
        statement_sort_key=stmt_key,
        text=text,
    )


def _classify_group(stmt_first_tok: tokenize.TokenInfo, *, text: str) -> int:
    # Group 1: bare `import ...`
    if stmt_first_tok.string == "import":
        return 1

    # For `from ... import ...`, parse the module segment conservatively.
    mod = _parse_from_module(text)
    if mod is None:
        return 2
    if mod.startswith("level_") and _LEVEL_RE.match(mod.split(".", 1)[0] or ""):
        # Only the exact `from level_N import ...` are group 3.
        if "." not in mod and _LEVEL_RE.match(mod):
            return 3
        return 2
    if mod.startswith(_GROUP_PREFIX_COMPETITION_INFRA):
        return 4
    if mod.startswith(_GROUP_PREFIX_CONTESTS):
        return 5
    return 2


def _module_sort_key(stmt_first_tok: tokenize.TokenInfo, *, text: str) -> tuple[object, ...]:
    if stmt_first_tok.string == "import":
        mod = _parse_import_module(text) or ""
    else:
        mod = _parse_from_module(text) or ""
    return _module_key_from_path(mod)


def _statement_sort_key(text: str) -> str:
    # Remove leading attached comments for a stable statement key.
    core = text.lstrip()
    while core.startswith("#"):
        nl = core.find("\n")
        if nl < 0:
            return ""
        core = core[nl + 1 :].lstrip()
    return core.strip()


def _module_key_from_path(module: str) -> tuple[object, ...]:
    parts = [p for p in module.split(".") if p]
    key: list[object] = []
    for p in parts:
        m = _LEVEL_RE.fullmatch(p)
        if m:
            key.append(("level", int(m.group(1))))
        else:
            key.append(("str", p))
    return tuple(key)


def _parse_import_module(text: str) -> str | None:
    # `import a.b as c` or `import a.b`
    s = text.lstrip()
    for ln in s.splitlines():
        stripped = ln.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("import "):
            rest = stripped[len("import ") :].strip()
            # Only use first module in multi-import; keeps ordering stable without splitting.
            first = rest.split(",", 1)[0].strip()
            first = first.split(" as ", 1)[0].strip()
            return first
        break
    return None


def _parse_from_module(text: str) -> str | None:
    s = text.lstrip()
    for ln in s.splitlines():
        stripped = ln.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("from "):
            rest = stripped[len("from ") :]
            mod = rest.split(" import ", 1)[0].strip()
            return mod or None
        break
    return None


def _render_grouped_items(items: Sequence[ImportOrganizerItem]) -> str:
    groups: dict[int, list[ImportOrganizerItem]] = {i: [] for i in range(1, 6)}
    for it in items:
        groups.setdefault(it.group, []).append(it)

    out_lines: list[str] = []
    for g in range(1, 6):
        chunk = groups.get(g) or []
        if not chunk:
            continue
        if out_lines:
            # exactly one blank line between groups
            if out_lines[-1].strip() != "":
                out_lines.append("\n")
            else:
                # collapse to exactly one blank line
                while len(out_lines) >= 2 and out_lines[-2].strip() == "":
                    out_lines.pop()
        for it in chunk:
            txt = it.text
            if not txt.endswith("\n"):
                txt += "\n"
            out_lines.append(txt)

    rendered = "".join(out_lines)
    # Ensure region ends with a single blank line if original had trailing blank lines handled
    return rendered

