"""Promotion/demotion suggestion analyzer (inbound usage by tier).

This analyzer is scope-aware and report-only. It normalizes imports to the local
`level_N.*` namespace for the configured scope, then counts inbound usage by
importer level to recommend promotion/demotion candidates.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from layers.layer_2_devtools.level_0_infra.level_0.base_health_analyzer import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    get_imports_from_ast,
    parse_file,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    file_to_module,
)
from layers.layer_2_devtools.level_0_infra.level_0.placement.promotion_demotion_suggestions import (
    HeavyReusePolicy,
    UsageEvidence,
    suggest_demotions,
    suggest_promotions,
)


_LEVEL_HEAD_RE = re.compile(r"^level_(\d+)$")
_LEVEL_SEG_RE = re.compile(r"(^|[.])level_(\d+)([.]|$)")


@dataclass(frozen=True)
class PromotionDemotionScopeConfig:
    scope: str  # general | contests | infra
    root: Path
    include: tuple[Path, ...] = ()
    exclude: tuple[Path, ...] = ()
    # Dotted prefixes that indicate scoped imports (strip to reach `level_N.*`).
    import_prefixes: tuple[str, ...] = ()
    heavy_reuse_policy: HeavyReusePolicy = HeavyReusePolicy()
    top_importers_limit: int = 10


class PromotionDemotionSuggestionAnalyzer(BaseAnalyzer):
    """Suggest promotion/demotion candidates based on inbound usage."""

    def __init__(self, root: Path, *, config: PromotionDemotionScopeConfig):
        super().__init__(root)
        self._cfg = config

    @property
    def name(self) -> str:
        return "promotion_demotion_suggestions"

    def analyze(self) -> dict[str, Any]:
        files = self._collect_files()

        module_level: dict[str, int | None] = {}
        module_by_file: dict[Path, str] = {}

        for fp in files:
            mod = file_to_module(fp, self.root)
            if not mod:
                continue
            module_by_file[fp] = mod
            module_level[mod] = _level_from_module_head(mod)

        # Add package nodes (e.g. `level_2`) so `from ... import` at package level counts.
        all_modules = _expand_with_package_nodes(module_level.keys())
        for m in all_modules:
            module_level.setdefault(m, _level_from_module_head(m))

        incoming: dict[str, list[UsageEvidence]] = {}

        for fp, importer in module_by_file.items():
            importer_level = module_level.get(importer)
            if importer_level is None:
                continue
            pkg = current_package(fp, self.root)
            tree = parse_file(fp)
            if tree is None or not isinstance(tree, ast.AST):
                continue
            imports = get_imports_from_ast(tree, pkg)
            for imported_mod in imports.keys():
                target = _normalize_import_to_scoped_module(
                    imported_mod,
                    import_prefixes=self._cfg.import_prefixes,
                )
                if target is None:
                    continue
                if target not in module_level:
                    # Accept package nodes for existing children, e.g. `level_2.x` -> `level_2`.
                    pkg_target = target.split(".", 1)[0]
                    if pkg_target in module_level:
                        target = pkg_target
                    else:
                        continue
                incoming.setdefault(target, []).append(
                    UsageEvidence(importer_module=importer, importer_level=int(importer_level))
                )

        promo_rows = suggest_promotions(
            modules=all_modules,
            module_level=module_level,
            incoming=incoming,
            policy=self._cfg.heavy_reuse_policy,
            top_importers_limit=int(self._cfg.top_importers_limit),
        )
        demo_rows = suggest_demotions(
            modules=all_modules,
            module_level=module_level,
            incoming=incoming,
            top_importers_limit=int(self._cfg.top_importers_limit),
        )

        counts = {
            "promotion": _count_status([r.status for r in promo_rows]),
            "demotion": _count_status([r.status for r in demo_rows]),
        }

        return {
            "scope": self._cfg.scope,
            "root": str(self.root.resolve()),
            "include": [str(p) for p in self._cfg.include],
            "exclude": [str(p) for p in self._cfg.exclude],
            "policy": {
                "heavy_reuse": {
                    "min_total_inbound": int(self._cfg.heavy_reuse_policy.min_total_inbound),
                    "min_distinct_importers": int(
                        self._cfg.heavy_reuse_policy.min_distinct_importers
                    ),
                    "min_distinct_levels": int(self._cfg.heavy_reuse_policy.min_distinct_levels),
                },
                "top_importers_limit": int(self._cfg.top_importers_limit),
            },
            "promotion_rows": [r.to_dict() for r in promo_rows],
            "demotion_rows": [r.to_dict() for r in demo_rows],
            "counts": counts,
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


def _normalize_import_to_scoped_module(
    imported_mod: str, *, import_prefixes: Iterable[str]
) -> str | None:
    """Normalize an import module string to `level_N...` within this scope."""
    if not imported_mod:
        return None

    # Direct `level_N` (general-style root alias).
    if imported_mod.startswith("level_") and _LEVEL_SEG_RE.search(imported_mod):
        return imported_mod

    # Strip configured prefixes (contest/infra and long general prefix).
    for pref in import_prefixes:
        if imported_mod.startswith(pref):
            tail = imported_mod[len(pref) :]
            if tail.startswith("level_") and _LEVEL_SEG_RE.search(tail):
                return tail

    return None


def _expand_with_package_nodes(modules: Iterable[str]) -> list[str]:
    out: set[str] = set()
    for m in modules:
        if not m:
            continue
        parts = [p for p in m.split(".") if p]
        if not parts:
            continue
        # Add all prefixes so package imports (`from level_2 import ...`) are represented.
        for i in range(1, len(parts) + 1):
            out.add(".".join(parts[:i]))
    return sorted(out)


def _count_status(statuses: Iterable[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for s in statuses:
        out[str(s)] = out.get(str(s), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: kv[0]))

