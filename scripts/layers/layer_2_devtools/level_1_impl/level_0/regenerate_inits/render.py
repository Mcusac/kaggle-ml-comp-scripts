"""Render deterministic `__init__.py` content."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderedInit:
    text: str
    kind: str  # "stub" | "leaf" | "aggregate" | "mixed"


def _header(doc: str) -> str:
    return f'"""{doc}"""\n'


def render_stub_init() -> RenderedInit:
    body = _header("Auto-generated package exports (empty).") + "\n" + "__all__: list[str] = []\n"
    return RenderedInit(text=body, kind="stub")


def render_leaf_init(module_to_symbols: dict[str, list[str]]) -> RenderedInit:
    """
    Render a leaf-package `__init__.py` that exports symbols from sibling modules explicitly.

    `module_to_symbols` should already exclude empty symbol lists.
    """
    if not module_to_symbols:
        return render_stub_init()

    modules = sorted(module_to_symbols.keys())
    lines: list[str] = [_header("Auto-generated package exports."), ""]

    exported: list[str] = []
    for mod in modules:
        symbols = sorted(set(module_to_symbols[mod]))
        if not symbols:
            continue
        exported.extend(symbols)
        if len(symbols) == 1:
            lines.append(f"from .{mod} import {symbols[0]}")
        else:
            lines.append(f"from .{mod} import (")
            for s in symbols:
                lines.append(f"    {s},")
            lines.append(")")
        lines.append("")

    exported = sorted(set(exported))
    lines.append("__all__ = [")
    for s in exported:
        lines.append(f'    "{s}",')
    lines.append("]")
    lines.append("")
    return RenderedInit(text="\n".join(lines), kind="leaf")


def render_aggregate_init(subpackages: list[str]) -> RenderedInit:
    """
    Render an aggregate `__init__.py` that re-exports subpackages via relative star imports
    and concatenates `__all__` from children.
    """
    kids = [k for k in subpackages if k and not k.startswith("_") and not k.startswith(".")]
    kids = sorted(set(kids))

    if not kids:
        return render_stub_init()

    lines: list[str] = [_header("Auto-generated aggregation exports."), ""]

    if len(kids) == 1:
        lines.append(f"from . import {kids[0]}")
    else:
        lines.append("from . import (")
        for k in kids:
            lines.append(f"    {k},")
        lines.append(")")
    lines.append("")

    for k in kids:
        lines.append(f"from .{k} import *")
    lines.append("")

    if len(kids) == 1:
        lines.append(f"__all__ = list({kids[0]}.__all__)")
    else:
        lines.append("__all__ = (")
        for i, k in enumerate(kids):
            prefix = "    " if i == 0 else "    + "
            lines.append(f"{prefix}list({k}.__all__)")
        lines.append(")")
    lines.append("")

    return RenderedInit(text="\n".join(lines), kind="aggregate")


def render_mixed_init(
    subpackages: list[str],
    module_to_symbols: dict[str, list[str]],
) -> RenderedInit:
    """
    Render a mixed `__init__.py` for packages that contain both:
    - subpackages (each with its own `__init__.py`), and
    - sibling modules that export public symbols.
    """
    kids = [k for k in subpackages if k and not k.startswith("_") and not k.startswith(".")]
    kids = sorted(set(kids))

    modules = sorted(module_to_symbols.keys())

    exported_module_symbols: list[str] = []
    for mod in modules:
        exported_module_symbols.extend(sorted(set(module_to_symbols.get(mod, []))))
    exported_module_symbols = sorted(set(exported_module_symbols))

    if not kids and not exported_module_symbols:
        return render_stub_init()

    if kids and not exported_module_symbols:
        return render_aggregate_init(kids)

    if not kids and exported_module_symbols:
        return render_leaf_init(module_to_symbols)

    lines: list[str] = [_header("Auto-generated mixed exports."), ""]

    if len(kids) == 1:
        lines.append(f"from . import {kids[0]}")
    else:
        lines.append("from . import (")
        for k in kids:
            lines.append(f"    {k},")
        lines.append(")")
    lines.append("")

    for k in kids:
        lines.append(f"from .{k} import *")
    lines.append("")

    for mod in modules:
        symbols = sorted(set(module_to_symbols.get(mod, [])))
        if not symbols:
            continue
        if len(symbols) == 1:
            lines.append(f"from .{mod} import {symbols[0]}")
        else:
            lines.append(f"from .{mod} import (")
            for s in symbols:
                lines.append(f"    {s},")
            lines.append(")")
        lines.append("")

    lines.append("__all__ = (")
    for i, k in enumerate(kids):
        prefix = "    " if i == 0 else "    + "
        lines.append(f"{prefix}list({k}.__all__)")
    lines.append("    + [")
    for s in exported_module_symbols:
        lines.append(f'        "{s}",')
    lines.append("    ]")
    lines.append(")")
    lines.append("")

    return RenderedInit(text="\n".join(lines), kind="mixed")

