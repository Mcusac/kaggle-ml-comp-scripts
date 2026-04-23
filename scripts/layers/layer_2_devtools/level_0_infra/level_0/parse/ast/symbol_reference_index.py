"""Build a conservative, alias-aware index of symbol references."""

import ast
from dataclasses import dataclass
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.models.symbol_reference_models import (
    SymbolReference,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    parse_file,
    resolve_relative_import,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    file_to_module,
)


@dataclass(frozen=True, slots=True)
class ReferenceIndexOptions:
    root: Path
    definitions_by_module: dict[str, set[str]]
    include_tests: bool = False


class ReferenceIndexBuilder:
    """
    Build a conservative reference index.

    Resolution rules (v1):
    - `from pkg.mod import Name as Alias` -> Alias resolves to `pkg.mod:Name`
    - `import pkg.mod as m` + `m.Name` -> resolves to `pkg.mod:Name`
    - `Name` within a module resolves to `current_module:Name` ONLY if Name is a known
      top-level definition in that module (avoids counting local variables).
    """

    def __init__(self, opts: ReferenceIndexOptions):
        self._opts = opts

    def build(self) -> list[SymbolReference]:
        out: list[SymbolReference] = []

        for file_path in collect_python_files(self._opts.root, include_tests=self._opts.include_tests):
            ref_module = file_to_module(file_path, self._opts.root)
            if not ref_module:
                continue

            tree = parse_file(file_path)
            if tree is None:
                continue

            pkg = current_package(file_path, self._opts.root)
            module_aliases, from_aliases = self._collect_import_aliases(tree, current_pkg=pkg)
            module_defs = self._opts.definitions_by_module.get(ref_module, set())

            out.extend(
                self._collect_references(
                    tree,
                    ref_module=ref_module,
                    ref_file=str(file_path),
                    module_aliases=module_aliases,
                    from_aliases=from_aliases,
                    module_defs=module_defs,
                )
            )

        return sorted(out, key=lambda r: (r.resolved_symbol_id, r.ref_module, r.ref_file, r.line, r.col))

    def _collect_import_aliases(
        self,
        tree: ast.AST,
        *,
        current_pkg: str,
    ) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
        module_aliases: dict[str, str] = {}
        from_aliases: dict[str, tuple[str, str]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local = alias.asname or alias.name.split(".")[0]
                    module_aliases[local] = alias.name
                continue

            if isinstance(node, ast.ImportFrom):
                level = getattr(node, "level", 0)
                resolved_mod = (
                    resolve_relative_import(level, current_pkg, node.module)
                    if level >= 1
                    else node.module
                )
                if not resolved_mod:
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    local = alias.asname or alias.name
                    from_aliases[local] = (resolved_mod, alias.name)

        return module_aliases, from_aliases

    def _collect_references(
        self,
        tree: ast.AST,
        *,
        ref_module: str,
        ref_file: str,
        module_aliases: dict[str, str],
        from_aliases: dict[str, tuple[str, str]],
        module_defs: set[str],
    ) -> list[SymbolReference]:
        out: list[SymbolReference] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in from_aliases:
                    mod, name = from_aliases[node.id]
                    out.append(
                        SymbolReference(
                            ref_module=ref_module,
                            ref_file=ref_file,
                            line=int(getattr(node, "lineno", 0) or 0),
                            col=int(getattr(node, "col_offset", 0) or 0),
                            resolved_symbol_id=f"{mod}:{name}",
                        )
                    )
                    continue

                if node.id in module_defs:
                    out.append(
                        SymbolReference(
                            ref_module=ref_module,
                            ref_file=ref_file,
                            line=int(getattr(node, "lineno", 0) or 0),
                            col=int(getattr(node, "col_offset", 0) or 0),
                            resolved_symbol_id=f"{ref_module}:{node.id}",
                        )
                    )
                    continue

            if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                base = node.value
                if isinstance(base, ast.Name) and base.id in module_aliases:
                    mod = module_aliases[base.id]
                    out.append(
                        SymbolReference(
                            ref_module=ref_module,
                            ref_file=ref_file,
                            line=int(getattr(node, "lineno", 0) or 0),
                            col=int(getattr(node, "col_offset", 0) or 0),
                            resolved_symbol_id=f"{mod}:{node.attr}",
                        )
                    )
                    continue

        return out

