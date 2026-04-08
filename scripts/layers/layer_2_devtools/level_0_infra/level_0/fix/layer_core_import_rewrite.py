"""Fix import styles for level_0 … level_10 under a ``layer_0_core`` tree.

Rules applied:
  __init__.py  → from level_N.pkg.module import X  →  from .module import X (relative)
               → import level_N.pkg as alias        →  from . import alias
  logic files  → from level_N.pkg.module import X where N == my_level AND pkg/module
                 is within my_pkg (sibling)          →  from .module import X (relative)
               → from level_N.pkg.module import X where N != my_level
                                                     →  from level_N import X (top-level API)
               → from level_N.pkg.module import X where N == my_level AND different subpkg
                                                     →  from level_N import X (top-level API)
"""

import re
from pathlib import Path

LEVEL_RE = re.compile(r"^level_\d+$")


def file_info(path: Path, scripts_root: Path) -> tuple[str | None, list[str]]:
    rel = path.relative_to(scripts_root)
    parts = rel.parts
    level = next((p for p in parts if LEVEL_RE.match(p)), None)
    pkg = list(parts[:-1])
    return level, pkg


def rewrite_line(line: str, is_init: bool, level: str, pkg: list[str]) -> str:
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]

    m = re.match(r"^from (level_\d+)((?:\.\w+)*) import (.+)", stripped)
    if m:
        src_level, src_rest, symbols = m.groups()

        if not src_rest:
            return line

        src_parts = [src_level] + src_rest.lstrip(".").split(".")

        if is_init:
            if src_parts[: len(pkg)] == pkg:
                rel_tail = ".".join(src_parts[len(pkg) :])
                return f"{indent}from .{rel_tail} import {symbols}\n"
            return line
        else:
            if src_level == level:
                if src_parts[: len(pkg)] == pkg:
                    rel_tail = ".".join(src_parts[len(pkg) :])
                    return f"{indent}from .{rel_tail} import {symbols}\n"
                else:
                    return f"{indent}from {level} import {symbols}\n"
            else:
                return f"{indent}from {src_level} import {symbols}\n"

    if is_init:
        m2 = re.match(r"^import (level_\d+)((?:\.\w+)+) as (\w+)", stripped)
        if m2:
            src_level, src_rest, alias = m2.groups()
            src_parts = [src_level] + src_rest.lstrip(".").split(".")
            if src_parts[:-1] == pkg:
                return f"{indent}from . import {alias}\n"

    return line


def process(path: Path, scripts_root: Path) -> int:
    level, pkg = file_info(path, scripts_root)
    if not level:
        return 0
    is_init = path.name == "__init__.py"

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    n = 0
    for ln in lines:
        new = rewrite_line(ln, is_init, level, pkg)
        if new != ln:
            n += 1
        out.append(new)
    if n:
        path.write_text("".join(out), encoding="utf-8")
    return n


def run_layer_core_import_rewrite(scripts_root: Path) -> int:
    """Rewrite imports under ``scripts_root`` (the ``layer_0_core`` directory)."""
    root = scripts_root.resolve()
    changed_files = 0
    total_changes = 0
    for i in range(11):
        level_root = root / f"level_{i}"
        if not level_root.is_dir():
            continue
        for path in sorted(level_root.rglob("*.py")):
            n = process(path, root)
            if n:
                changed_files += 1
                total_changes += n
                print(f"  {path.relative_to(root)} ({n})")
    print(f"\n✅ {changed_files} files, {total_changes} line changes")
    return 0
