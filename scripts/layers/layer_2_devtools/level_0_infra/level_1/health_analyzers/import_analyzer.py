"""Import dependency analyzer."""

import ast
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.base_health_analyzer import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    get_imports_from_file,
    parse_file,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    discover_packages,
    file_to_module,
    is_internal_module,
)


class ImportAnalyzer(BaseAnalyzer):
    """
    Analyze import dependencies and relationships.
    
    Provides:
    - Import map (who imports what)
    - Deep imports (depth >= 4)
    - Cross-package imports
    - Incoming dependencies
    - Orphaned modules
    """
    
    @property
    def name(self) -> str:
        return "imports"
    
    def analyze(self) -> dict[str, Any]:
        """Analyze import dependencies."""
        files = collect_python_files(self.root)
        internal_packages = discover_packages(self.root)
        
        file_imports = self._collect_file_imports(files)
        internal_deps, incoming = self._build_internal_dependencies(file_imports, internal_packages)
        deep_imports, deep_cross_package = self._find_deep_imports(internal_deps)
        orphans = self._find_orphans(file_imports, incoming, internal_packages)
        
        return {
            'import_map': {mod: sorted(deps) for mod, deps in internal_deps.items()},
            'deep_imports': deep_imports,
            'deep_cross_package': deep_cross_package,
            'incoming': {k: sorted(v) for k, v in incoming.items()},
            'orphans': orphans,
        }
    
    def _collect_file_imports(self, files: list) -> dict[str, dict[str, set[str]]]:
        """Collect all imports from files."""
        file_imports: dict[str, dict[str, set[str]]] = {}
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            pkg = current_package(file_path, self.root)
            imports = get_imports_from_file(file_path, pkg)
            file_imports[module] = imports
        
        return file_imports
    
    def _build_internal_dependencies(
        self, 
        file_imports: dict[str, dict[str, set[str]]],
        internal_packages: set[str]
    ) -> tuple[dict[str, list[str]], dict[str, set[str]]]:
        """Build internal dependency graph and incoming dependencies."""
        internal_deps: dict[str, list[str]] = {}
        incoming: dict[str, set[str]] = {}
        
        for importer, deps in file_imports.items():
            internal_list = [
                d for d in deps
                if is_internal_module(d, internal_packages)
            ]
            internal_deps[importer] = internal_list
            
            for dep in internal_list:
                incoming.setdefault(dep, set()).add(importer)
        
        return internal_deps, incoming
    
    def _find_deep_imports(
        self, 
        internal_deps: dict[str, list[str]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Find deep imports (depth >= 4) and cross-package deep imports."""
        deep_imports = []
        deep_cross_package = []
        
        for importer, deps in internal_deps.items():
            importer_pkg = importer.split('.')[0]
            
            for dep in deps:
                parts = dep.split('.')
                depth = len(parts)
                
                if depth >= 4:
                    is_cross_package = importer_pkg != parts[0]
                    
                    import_info = {
                        'importer': importer,
                        'imported': dep,
                        'depth': depth,
                        'cross_package': is_cross_package
                    }
                    
                    deep_imports.append(import_info)
                    
                    if is_cross_package:
                        deep_cross_package.append(import_info)
        
        return deep_imports, deep_cross_package
    
    def _find_orphans(
        self,
        file_imports: dict[str, dict[str, set[str]]],
        incoming: dict[str, set[str]],
        internal_packages: set[str]
    ) -> list[str]:
        """Find orphaned modules (no incoming dependencies, excluding intentional ones)."""
        all_internal = {
            m for m in file_imports
            if is_internal_module(m, internal_packages)
        }
        
        excluded = self._get_intentional_orphans(all_internal)
        
        orphans = sorted([
            m for m in all_internal
            if m not in excluded and m not in incoming
        ])
        
        return orphans
    
    def _get_intentional_orphans(self, all_internal: set[str]) -> set[str]:
        """Get modules that are intentionally orphaned (not imported directly)."""
        # Entry points and __init__ modules (package namespaces)
        entry_points = {'run', '__init__'}
        roots_ok = {
            m for m in all_internal
            if m.split('.')[-1] in entry_points or m == 'run'
        }
        
        # Contest implementations (loaded via registry pattern)
        registry_loaded = {
            m for m in all_internal
            if m.startswith('contest.implementations.') and not m.endswith('.__init__')
        }
        
        # CLI modules (loaded dynamically by router)
        cli_modules = {
            m for m in all_internal
            if m.endswith('.cli') or '.cli.' in m
        }
        
        # Modules that export via __all__ (package API modules)
        package_api_modules = self._find_package_api_modules()
        
        return roots_ok | registry_loaded | cli_modules | package_api_modules
    
    def _find_package_api_modules(self) -> set[str]:
        """Find modules that export via __all__ (package API modules)."""
        package_api_modules = set()
        files = collect_python_files(self.root)
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            tree = parse_file(file_path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == '__all__':
                                package_api_modules.add(module)
                                break
        
        return package_api_modules
