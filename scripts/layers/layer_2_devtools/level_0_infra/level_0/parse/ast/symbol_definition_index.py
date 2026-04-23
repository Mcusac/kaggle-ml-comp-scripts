"""Build an index of top-level symbol definitions across a tree."""

import ast
from dataclasses import dataclass
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.models.symbol_models import (
    SymbolDefinition,
    SymbolKind,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.public_symbols import (
    DEFAULT_EXCLUDED_SYMBOLS,
    is_public_symbol,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    file_to_module,
)


@dataclass(frozen=True, slots=True)
class DefinitionIndexOptions:
    root: Path
    include_tests: bool = False
    excluded_symbols: set[str] | None = None


class DefinitionIndexBuilder:
    """Collect top-level symbol definitions with spans and stable IDs."""

    def __init__(self, opts: DefinitionIndexOptions):
        self._opts = opts

    def build(self) -> list[SymbolDefinition]:
        excluded = (
            set(DEFAULT_EXCLUDED_SYMBOLS)
            if self._opts.excluded_symbols is None
            else set(self._opts.excluded_symbols)
        )

        out: list[SymbolDefinition] = []
        for file_path in collect_python_files(self._opts.root, include_tests=self._opts.include_tests):
            module = file_to_module(file_path, self._opts.root)
            if not module:
                continue

            tree = parse_file(file_path)
            if tree is None:
                continue

            out.extend(
                self._defs_from_tree(
                    tree,
                    module=module,
                    file_path=file_path,
                    excluded=excluded,
                )
            )

        return sorted(out, key=lambda d: (d.module, d.qualname, d.kind.value, d.file, d.line_start))

    def _defs_from_tree(
        self,
        tree: ast.AST,
        *,
        module: str,
        file_path: Path,
        excluded: set[str],
    ) -> list[SymbolDefinition]:
        defs: list[SymbolDefinition] = []

        for node in getattr(tree, "body", []):
            if isinstance(node, ast.ClassDef):
                defs.append(
                    self._mk_def(
                        module=module,
                        qualname=node.name,
                        kind=SymbolKind.CLASS,
                        node=node,
                        file_path=file_path,
                        excluded=excluded,
                    )
                )
                continue

            if isinstance(node, ast.FunctionDef):
                defs.append(
                    self._mk_def(
                        module=module,
                        qualname=node.name,
                        kind=SymbolKind.FUNCTION,
                        node=node,
                        file_path=file_path,
                        excluded=excluded,
                    )
                )
                continue

            if isinstance(node, ast.AsyncFunctionDef):
                defs.append(
                    self._mk_def(
                        module=module,
                        qualname=node.name,
                        kind=SymbolKind.ASYNC_FUNCTION,
                        node=node,
                        file_path=file_path,
                        excluded=excluded,
                    )
                )
                continue

            if isinstance(node, ast.Assign):
                if len(node.targets) != 1:
                    continue
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    defs.append(
                        self._mk_def(
                            module=module,
                            qualname=target.id,
                            kind=SymbolKind.CONSTANT,
                            node=node,
                            file_path=file_path,
                            excluded=excluded,
                        )
                    )
                continue

            if isinstance(node, ast.AnnAssign):
                target = node.target
                if isinstance(target, ast.Name):
                    defs.append(
                        self._mk_def(
                            module=module,
                            qualname=target.id,
                            kind=SymbolKind.CONSTANT,
                            node=node,
                            file_path=file_path,
                            excluded=excluded,
                        )
                    )
                continue

        return [d for d in defs if d.qualname and d.is_public]

    def _mk_def(
        self,
        *,
        module: str,
        qualname: str,
        kind: SymbolKind,
        node: ast.AST,
        file_path: Path,
        excluded: set[str],
    ) -> SymbolDefinition:
        line_start = int(getattr(node, "lineno", 0) or 0)
        line_end = int(getattr(node, "end_lineno", 0) or line_start or 0)
        public = is_public_symbol(qualname, excluded=excluded)
        return SymbolDefinition(
            module=module,
            qualname=qualname,
            kind=kind,
            file=str(file_path),
            line_start=line_start,
            line_end=line_end,
            is_public=public,
        )

