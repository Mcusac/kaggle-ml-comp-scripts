from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class _FileText:
    text: str
    newline: str


@dataclass(frozen=True)
class SpanEditOperation:
    """A single, safe replacement for a contiguous line span (1-indexed)."""

    path: Path
    start_line: int
    end_line_excl: int
    kind: str
    old_text: str
    new_text: str


@dataclass(frozen=True)
class SpanEditResult:
    path: Path
    applied: bool
    kind: str


@dataclass(frozen=True)
class SpanFixRunSummary:
    files_considered: int
    files_changed: int
    edits_applied: int


def _read_text_preserve_newlines(path: Path) -> _FileText:
    data = path.read_bytes()
    text = data.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return _FileText(text=text, newline=newline)


def _write_text_with_newlines(path: Path, text: str, newline: str) -> None:
    normalized = text.replace("\r\n", "\n")
    if newline == "\r\n":
        normalized = normalized.replace("\n", "\r\n")
    path.write_text(normalized, encoding="utf-8")


def apply_span_edit_operations(
    ops: Iterable[SpanEditOperation],
    *,
    apply: bool,
    max_changes_per_file: int,
) -> tuple[list[SpanEditResult], SpanFixRunSummary, list[str]]:
    by_file: dict[Path, list[SpanEditOperation]] = {}
    for op in ops:
        by_file.setdefault(op.path, []).append(op)

    results: list[SpanEditResult] = []
    errors: list[str] = []
    files_considered = len(by_file)
    files_changed = 0
    edits_applied = 0

    for path in sorted(by_file.keys(), key=lambda p: p.as_posix()):
        ops_for_file = sorted(
            by_file[path], key=lambda o: (o.start_line, o.end_line_excl, o.kind)
        )
        if len(ops_for_file) > max_changes_per_file:
            errors.append(
                f"Refusing to edit {path.as_posix()}: "
                f"edits={len(ops_for_file)} exceeds --max-changes-per-file={max_changes_per_file}"
            )
            continue
        if not path.is_file():
            errors.append(f"Missing file: {path.as_posix()}")
            continue

        ft = _read_text_preserve_newlines(path)
        lines = ft.text.replace("\r\n", "\n").splitlines(keepends=True)
        file_changed = False

        for op in ops_for_file:
            if op.start_line <= 0 or op.start_line > len(lines) + 1:
                errors.append(
                    f"Out-of-range start_line for {path.as_posix()}: start_line={op.start_line} kind={op.kind}"
                )
                results.append(SpanEditResult(path=path, applied=False, kind=op.kind))
                continue
            if op.end_line_excl < op.start_line or op.end_line_excl > len(lines) + 1:
                errors.append(
                    f"Out-of-range end_line_excl for {path.as_posix()}: end_line_excl={op.end_line_excl} kind={op.kind}"
                )
                results.append(SpanEditResult(path=path, applied=False, kind=op.kind))
                continue

            start_idx0 = op.start_line - 1
            end_idx0_excl = op.end_line_excl - 1
            current = "".join(lines[start_idx0:end_idx0_excl])
            if current != op.old_text:
                errors.append(
                    f"Edit drift for {path.as_posix()}:{op.start_line}-{op.end_line_excl} kind={op.kind}\n"
                    f"expected:\n{op.old_text!r}\n"
                    f"found:\n{current!r}"
                )
                results.append(SpanEditResult(path=path, applied=False, kind=op.kind))
                continue

            replacement = op.new_text
            if replacement and not replacement.endswith("\n") and current.endswith("\n"):
                replacement += "\n"

            lines[start_idx0:end_idx0_excl] = [replacement]
            file_changed = True
            edits_applied += 1
            results.append(SpanEditResult(path=path, applied=True, kind=op.kind))

        if file_changed:
            files_changed += 1
            if apply:
                _write_text_with_newlines(path, "".join(lines), ft.newline)

    summary = SpanFixRunSummary(
        files_considered=files_considered,
        files_changed=files_changed,
        edits_applied=edits_applied,
    )
    return results, summary, errors

