"""Import path validator for detecting incorrect relative import paths."""

from typing import Any
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.base_health_analyzer import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    discover_packages,
    file_to_module,
    is_internal_module,
    module_exists,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    get_relative_imports_from_ast,
    parse_file,
    resolve_relative_import,
)


class ImportPathValidator(BaseAnalyzer):
    """
    Validate that relative import paths resolve to existing modules.
    
    Detects incorrect relative imports like:
    - `from ...testing` when it should be `from ..testing`
    - `from ..cv_splits` when it should be `from .cv_splits`
    
    Only validates internal modules (modules within the codebase).
    External dependencies are not validated as they may not be installed.
    """
    
    def __init__(self, root: Path, include_tests: bool = False):
        super().__init__(root)
        self._include_tests = bool(include_tests)

    @property
    def name(self) -> str:
        return "import_paths"
    
    def analyze(self) -> dict[str, Any]:
        """Validate all relative import paths in the codebase."""
        files = collect_python_files(self.root, include_tests=self._include_tests)
        internal_packages = discover_packages(self.root)
        
        invalid_imports = []
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            current_pkg = current_package(file_path, self.root)
            
            # Parse file and get relative imports
            tree = parse_file(file_path)
            if not tree:
                continue
            
            relative_imports = get_relative_imports_from_ast(tree, current_pkg)
            
            for rel_import in relative_imports:
                resolved_name = rel_import['resolved_name']
                
                # Skip if resolved name is None (invalid syntax)
                if not resolved_name:
                    continue
                
                # Only validate internal modules
                if not is_internal_module(resolved_name, internal_packages):
                    continue
                
                # Check if module exists
                if not module_exists(resolved_name, self.root):
                    # Try to suggest correct import
                    suggested = self._suggest_correct_import(
                        file_path, rel_import, current_pkg, internal_packages
                    )
                    
                    invalid_imports.append({
                        'file': module,
                        'line': rel_import['line_number'],
                        'original': rel_import['original_syntax'],
                        'resolved': resolved_name,
                        'suggested': suggested
                    })
        
        return {
            'invalid_imports': invalid_imports,
            'total_invalid': len(invalid_imports)
        }
    
    def _suggest_correct_import(
        self,
        file_path: Path,
        rel_import: dict,
        current_pkg: str,
        internal_packages: set[str]
    ) -> str | None:
        """
        Suggest a correct import path if possible.
        
        Args:
            file_path: Path to file with invalid import
            rel_import: Relative import metadata
            current_pkg: Current package name
            internal_packages: Set of internal package names
            
        Returns:
            Suggested import statement or None if cannot determine
        """
        module_name = rel_import['module']
        if not module_name:
            return None
        
        # Get the directory of the current file
        file_dir = file_path.parent
        
        for level in [1, 2, 3, 4]:
            if level == rel_import['level']:
                continue  # Skip the incorrect level we already tried

            test_resolved = resolve_relative_import(level, current_pkg, module_name)
            if test_resolved and is_internal_module(test_resolved, internal_packages):
                if module_exists(test_resolved, self.root):
                    dots = '.' * level
                    return f"from {dots}{module_name} import ..."
        
        # Try checking if module exists in same directory (level 1)
        same_dir_module = file_dir / f"{module_name}.py"
        if same_dir_module.exists():
            return f"from .{module_name} import ..."
        
        # Try checking if module exists in parent directory (level 2)
        parent_dir = file_dir.parent
        parent_module = parent_dir / f"{module_name}.py"
        if parent_module.exists():
            parent_pkg = '.'.join(current_pkg.split('.')[:-1]) if current_pkg else ""
            if parent_pkg:
                return f"from ..{module_name} import ..."
        
        return None
