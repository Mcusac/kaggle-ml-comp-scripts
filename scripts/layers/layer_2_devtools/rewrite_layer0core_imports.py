from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


LAYER0CORE_REL = Path("input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core")

FROM_LEVEL_RE = re.compile(r"^(?P<indent>[ \t]*)from[ \t]+level_(?P<n>\d+)[ \t]+import[ \t]+", re.MULTILINE)
IMPORT_LEVEL_RE = re.compile(r"^(?P<indent>[ \t]*)import[ \t]+level_(?P<n>\d+)\b", re.MULTILINE)


@dataclass(frozen=True)
class FileChange:
    path: Path
    from_level_rewrites: int
    import_level_rewrites: int


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        yield path


def _rewrite_contents(src: str) -> tuple[str, int, int]:
    from_count = 0
    import_count = 0

    def _from_repl(m: re.Match[str]) -> str:
        nonlocal from_count
        from_count += 1
        indent = m.group("indent")
        n = m.group("n")
        return f"{indent}from layers.layer_0_core.level_{n} import "

    def _import_repl(m: re.Match[str]) -> str:
        nonlocal import_count
        import_count += 1
        indent = m.group("indent")
        n = m.group("n")
        return f"{indent}import layers.layer_0_core.level_{n} as level_{n}"

    out = FROM_LEVEL_RE.sub(_from_repl, src)
    out = IMPORT_LEVEL_RE.sub(_import_repl, out)
    return out, from_count, import_count


def _read_text_preserve_newlines(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    text = data.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, newline


def _write_text_with_newlines(path: Path, text: str, newline: str) -> None:
    normalized = text.replace("\r\n", "\n")
    if newline == "\r\n":
        normalized = normalized.replace("\n", "\r\n")
    path.write_text(normalized, encoding="utf-8")


def rewrite_tree(root: Path, *, apply: bool) -> list[FileChange]:
    changes: list[FileChange] = []
    for py in sorted(_iter_python_files(root)):
        original, newline = _read_text_preserve_newlines(py)
        rewritten, from_count, import_count = _rewrite_contents(original)
        if rewritten == original:
            continue
        changes.append(FileChange(py, from_count, import_count))
        if apply:
            _write_text_with_newlines(py, rewritten, newline)
    return changes


def _summarize(changes: Sequence[FileChange]) -> str:
    total_from = sum(c.from_level_rewrites for c in changes)
    total_import = sum(c.import_level_rewrites for c in changes)
    lines = [
        f"changed_files={len(changes)}",
        f"from_level_rewrites={total_from}",
        f"import_level_rewrites={total_import}",
        "files:",
    ]
    for c in changes:
        lines.append(f"- {c.path.as_posix()} (from={c.from_level_rewrites}, import={c.import_level_rewrites})")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rewrite layer_0_core unqualified level imports.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd() / LAYER0CORE_REL,
        help="Path to layer_0_core directory.",
    )
    parser.add_argument("--apply", action="store_true", help="Apply edits (default is dry-run).")
    args = parser.parse_args(argv)

    root: Path = args.root
    if not root.exists():
        raise FileNotFoundError(f"Root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Root is not a directory: {root}")

    changes = rewrite_tree(root, apply=args.apply)
    print(_summarize(changes), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

