from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from layers.layer_2_devtools.level_0_infra.level_0.fix.import_fix_models import (
    EditOperation,
    FileEditResult,
    FixRunSummary,
)


@dataclass(frozen=True)
class _FileText:
    text: str
    newline: str


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


def apply_edit_operations(
    ops: Iterable[EditOperation],
    *,
    apply: bool,
    max_changes_per_file: int,
) -> tuple[list[FileEditResult], FixRunSummary, list[str]]:
    by_file: dict[Path, list[EditOperation]] = {}
    for op in ops:
        by_file.setdefault(op.path, []).append(op)

    results: list[FileEditResult] = []
    errors: list[str] = []
    files_considered = len(by_file)
    files_changed = 0
    edits_applied = 0

    for path in sorted(by_file.keys(), key=lambda p: p.as_posix()):
        ops_for_file = sorted(by_file[path], key=lambda o: (o.line, o.kind))
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
        lines = ft.text.splitlines(keepends=True)
        applied_here = 0

        for op in ops_for_file:
            if op.line <= 0 or op.line > len(lines):
                errors.append(
                    f"Out-of-range line for {path.as_posix()}: line={op.line} kind={op.kind}"
                )
                continue

            current = lines[op.line - 1]
            if current != op.old_line:
                # Safe failure: do not guess.
                errors.append(
                    f"Edit drift for {path.as_posix()}:{op.line} kind={op.kind}\n"
                    f"expected: {op.old_line!r}\n"
                    f"found:    {current!r}"
                )
                continue

            lines[op.line - 1] = op.new_line
            applied_here += 1

        if applied_here:
            edits_applied += applied_here
            files_changed += 1
            if apply:
                _write_text_with_newlines(path, "".join(lines), ft.newline)
        results.append(FileEditResult(path=path, edits_applied=applied_here))

    summary = FixRunSummary(
        files_considered=files_considered,
        files_changed=files_changed,
        edits_applied=edits_applied,
    )
    return results, summary, errors

