"""Build the machine-generated inventory markdown fragment (tree + per-file AST summary)."""

from __future__ import annotations

import ast
from pathlib import Path


def _static_all_from_tree(tree: ast.Module) -> list[str] | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    elts = node.value
                    if isinstance(elts, (ast.List, ast.Tuple)):
                        out: list[str] = []
                        for elt in elts.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                out.append(elt.value)
                        return out
    return None


def _format_imports(tree: ast.Module) -> list[str]:
    lines: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                lines.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            names = ", ".join(
                a.name if not a.asname else f"{a.name} as {a.asname}"
                for a in node.names
            )
            if node.level:
                mod = "." * node.level + (node.module or "")
            else:
                mod = node.module or ""
            lines.append(f"from {mod} import {names}")
    return lines


def bootstrap_markdown(level_path: Path, workspace: Path | None) -> str:
    root = level_path.resolve()
    if not root.is_dir():
        raise SystemExit("--level-path must be a directory")

    lines: list[str] = [
        "## Machine-generated (verify)",
        "",
        "_Planner: merge into inventory; verify signatures and flags against source._",
        "",
    ]
    if workspace:
        try:
            rel_root = root.relative_to(workspace.resolve())
            lines.append(f"**Relative to workspace:** `{rel_root.as_posix()}`")
            lines.append("")
        except ValueError:
            pass

    lines.extend(
        [
            "### Package tree",
            "",
            "```",
        ]
    )

    def walk(d: Path, prefix: str = "") -> None:
        subs = sorted(
            [p for p in d.iterdir() if p.name != "__pycache__"],
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
        for i, p in enumerate(subs):
            last = i == len(subs) - 1
            branch = "└── " if last else "├── "
            lines.append(f"{prefix}{branch}{p.name}")
            if p.is_dir():
                ext = "    " if last else "│   "
                walk(p, prefix + ext)

    walk(root)
    lines.append("```")
    lines.append("")

    py_files = sorted(root.rglob("*.py"))
    for py in py_files:
        rel = py.relative_to(root)
        try:
            text = py.read_text(encoding="utf-8")
            lc = len(text.splitlines())
            tree = ast.parse(text, filename=str(py))
        except (SyntaxError, OSError) as e:
            lines.append(f"### FILE: {rel.as_posix()} (parse error: {e})")
            lines.append("")
            continue

        lines.append(f"### FILE: {rel.as_posix()}")
        lines.append(f"- Line count: {lc}")
        all_names = _static_all_from_tree(tree)
        if all_names is not None:
            lines.append(f"- __all__ (static): {', '.join(all_names)}")
        lines.append("- Imports (top-level, AST order):")
        imps = _format_imports(tree)
        if not imps:
            lines.append("  - _(none)_")
        else:
            for imp in imps:
                lines.append(f"  - `{imp}`")
        lines.append("")

    return "\n".join(lines)
