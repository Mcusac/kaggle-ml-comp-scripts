"""File level suggestion analyzer (minimal valid tier with constraints).

This is report-only and intentionally filesystem/AST-based (no runtime importing).
It reuses module discovery and import extraction primitives.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from layers.layer_2_devtools.level_0_infra.level_0.base_health_analyzer import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    get_imports_from_ast,
    parse_file,
    resolve_relative_import,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    file_to_module,
)
from layers.layer_2_devtools.level_0_infra.level_0.placement.file_level_suggestions import (
    Evidence,
    FileLevelSuggestionRow,
    LevelPolicy,
    suggest_levels,
)


_LEVEL_HEAD_RE = re.compile(r"^level_(\d+)$")
_LEVEL_SEG_RE = re.compile(r"(^|[.])level_(\d+)([.]|$)")


@dataclass(frozen=True)
class ScopeConfig:
    scope: str  # general | contests | infra
    root: Path
    include: tuple[Path, ...] = ()
    exclude: tuple[Path, ...] = ()
    # Dotted prefixes that indicate scoped level modules in imports.
    # Example: general supports "level_3" and "layers.layer_0_core.level_3".
    import_prefixes: tuple[str, ...] = ()
    policy: LevelPolicy = LevelPolicy(min_level_delta_for_outgoing=1, max_level_delta_for_incoming=-1)


class FileLevelSuggestionAnalyzer(BaseAnalyzer):
    """Compute minimal valid levels and conflicts for a scope root."""

    def __init__(self, root: Path, *, config: ScopeConfig):
        super().__init__(root)
        self._cfg = config

    @property
    def name(self) -> str:
        return "file_level_suggestions"

    def analyze(self) -> dict[str, Any]:
        files = self._collect_files()
        module_by_file: dict[Path, str] = {}
        file_by_module: dict[str, Path] = {}
        module_level: dict[str, int | None] = {}

        outgoing_refs: dict[str, list[Evidence]] = {}
        incoming_refs: dict[str, list[Evidence]] = {}

        for fp in files:
            mod = file_to_module(fp, self.root)
            if not mod:
                continue
            module_by_file[fp] = mod
            file_by_module[mod] = fp
            module_level[mod] = _level_from_module_head(mod)

        # Collect outgoing import evidence per module.
        for fp, mod in module_by_file.items():
            pkg = current_package(fp, self.root)
            tree = parse_file(fp)
            if tree is None or not isinstance(tree, ast.AST):
                continue
            imports = get_imports_from_ast(tree, pkg)
            for imported_mod in imports.keys():
                ref = _extract_scoped_level_ref(
                    imported_mod,
                    import_prefixes=self._cfg.import_prefixes,
                )
                if ref is None:
                    continue
                outgoing_refs.setdefault(mod, []).append(
                    Evidence(
                        module=mod,
                        referenced=imported_mod,
                        referenced_level=ref,
                    )
                )

        # Build incoming evidence by inverting outgoing edges (only level refs).
        for mod, refs in outgoing_refs.items():
            src_level = module_level.get(mod)
            if src_level is None:
                continue
            for _ref in refs:
                # Determine the referenced module level, but we don't know exact file module;
                # incoming constraint uses *importer* level.
                # Store importer level in `referenced_level`.
                target_mod = _scoped_target_module_hint(_ref.referenced, import_prefixes=self._cfg.import_prefixes)
                if target_mod is None:
                    continue
                incoming_refs.setdefault(target_mod, []).append(
                    Evidence(
                        module=mod,
                        referenced=_ref.referenced,
                        referenced_level=src_level,
                    )
                )

        all_modules = set(module_level.keys()) | set(incoming_refs.keys())
        rows = suggest_levels(
            modules=all_modules,
            module_level=module_level,
            outgoing_level_refs=outgoing_refs,
            incoming_level_refs=incoming_refs,
            policy=self._cfg.policy,
        )

        return {
            "scope": self._cfg.scope,
            "root": str(self.root.resolve()),
            "include": [str(p) for p in self._cfg.include],
            "exclude": [str(p) for p in self._cfg.exclude],
            "policy": {
                "min_level_delta_for_outgoing": self._cfg.policy.min_level_delta_for_outgoing,
                "max_level_delta_for_incoming": self._cfg.policy.max_level_delta_for_incoming,
            },
            "rows": [r.to_dict() for r in rows],
            "counts": _count_rows(rows),
        }

    def _collect_files(self) -> list[Path]:
        files = collect_python_files(self.root, include_tests=False)
        if self._cfg.include:
            includes = tuple(p.resolve() for p in self._cfg.include)
            files = [p for p in files if any(_is_under(p, inc) for inc in includes)]
        if self._cfg.exclude:
            excludes = tuple(p.resolve() for p in self._cfg.exclude)
            files = [p for p in files if not any(_is_under(p, exc) for exc in excludes)]
        return files


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _level_from_module_head(module: str) -> int | None:
    head = module.split(".", 1)[0]
    m = _LEVEL_HEAD_RE.fullmatch(head)
    return int(m.group(1)) if m else None


def _extract_scoped_level_ref(imported_mod: str, *, import_prefixes: Iterable[str]) -> int | None:
    """Return referenced level int if import string indicates a scope level surface."""
    if not imported_mod:
        return None
    # Accept raw 'level_N' and 'level_N.*' always.
    m = _LEVEL_SEG_RE.search(imported_mod)
    if m and imported_mod.startswith("level_"):
        return int(m.group(2))
    # Accept configured prefixes, e.g. 'layers.layer_0_core.' then '.level_N'.
    for pref in import_prefixes:
        if imported_mod.startswith(pref):
            m2 = _LEVEL_SEG_RE.search(imported_mod[len(pref) :])
            if m2:
                return int(m2.group(2))
    return None


def _scoped_target_module_hint(imported_mod: str, *, import_prefixes: Iterable[str]) -> str | None:
    """Best-effort map import string to a module name within this analyzer root.

    We only need the *level_N* package (e.g. 'level_3') for incoming constraints.
    """
    if not imported_mod:
        return None
    if imported_mod.startswith("level_"):
        return imported_mod.split(".", 1)[0]
    for pref in import_prefixes:
        if imported_mod.startswith(pref):
            tail = imported_mod[len(pref) :]
            if tail.startswith("level_"):
                return tail.split(".", 1)[0]
    return None


def _count_rows(rows: Iterable[FileLevelSuggestionRow]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        out[r.status] = out.get(r.status, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: kv[0]))

