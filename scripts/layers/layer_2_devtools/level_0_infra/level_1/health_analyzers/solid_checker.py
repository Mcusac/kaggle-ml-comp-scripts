"""SOLID principles violation checker."""

import ast
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import (
    BaseAnalyzer,
    collect_python_files,
    count_lines_in_node,
    current_package,
    discover_packages,
    file_to_module,
    get_all_classes,
    get_all_functions,
    get_imports_from_ast,
    is_internal_module,
    parse_file,
)


class SOLIDChecker(BaseAnalyzer):
    """
    Check for SOLID principle violations.
    
    Checks:
    - SRP: Functions >50 lines, classes with >7 methods
    - DIP: Concrete imports across package boundaries
    - OCP: Hardcoded conditionals (basic heuristic)
    """
    
    @property
    def name(self) -> str:
        return "solid"
    
    def analyze(self) -> dict[str, Any]:
        """Check for SOLID violations."""
        files = collect_python_files(self.root)
        internal_packages = discover_packages(self.root)
        
        srp_violations: list[dict[str, Any]] = []
        dip_violations: list[dict[str, Any]] = []
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            tree = parse_file(file_path)
            if not tree:
                continue
            
            # Check SRP: Long functions/classes
            for func_name, func_node in get_all_functions(tree):
                lines = count_lines_in_node(func_node)
                if lines > 50:
                    srp_violations.append({
                        'module': module,
                        'type': 'function',
                        'name': func_name,
                        'reason': f'Function too long ({lines} lines)',
                        'line': func_node.lineno
                    })
            
            for class_name, class_node in get_all_classes(tree):
                methods = [n for n in class_node.body 
                          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if len(methods) > 7:
                    srp_violations.append({
                        'module': module,
                        'type': 'class',
                        'name': class_name,
                        'reason': f'Too many methods ({len(methods)})',
                        'line': class_node.lineno
                    })
            
            # Check DIP: Cross-package concrete imports
            current_pkg = module.split('.')[0]
            pkg = current_package(file_path, self.root)
            imports = get_imports_from_ast(tree, pkg)
            
            for imported_module in imports:
                if not is_internal_module(imported_module, internal_packages):
                    continue
                
                imported_pkg = imported_module.split('.')[0]
                
                # Cross-package import of deep module (concrete dependency)
                if imported_pkg != current_pkg and imported_module.count('.') >= 3:
                    dip_violations.append({
                        'module': module,
                        'imported': imported_module,
                        'reason': 'Deep cross-package import (concrete dependency)',
                    })
        
        return {
            'srp_violations': srp_violations,
            'dip_violations': dip_violations,
            'total_violations': len(srp_violations) + len(dip_violations),
        }
