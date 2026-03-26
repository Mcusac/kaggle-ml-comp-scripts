"""File metrics analyzer for line counts and basic statistics."""

import ast
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import (
    BaseAnalyzer,
    collect_python_files,
    count_lines_in_node,
    file_to_module,
    get_all_classes,
    get_all_functions,
    parse_file,
)
from layers.layer_2_devtools.level_0_infra.level_0.io import text_file as file_utils


class FileMetricsAnalyzer(BaseAnalyzer):
    """
    Analyze file-level metrics.
    
    Checks:
    - File line counts
    - Function line counts
    - Class method counts
    """
    
    @property
    def name(self) -> str:
        return "file_metrics"
    
    def analyze(self) -> dict[str, Any]:
        """Analyze file metrics."""
        files = collect_python_files(self.root)
        
        file_lines: dict[str, int] = {}
        long_functions: list[dict[str, Any]] = []
        large_classes: list[dict[str, Any]] = []
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            # Count file lines
            lines = file_utils.count_lines(file_path)
            file_lines[module] = lines
            
            # Analyze functions and classes
            tree = parse_file(file_path)
            if tree:
                # Check function lengths
                for func_name, func_node in get_all_functions(tree):
                    func_lines = count_lines_in_node(func_node)
                    if func_lines > 50:
                        long_functions.append({
                            'module': module,
                            'function': func_name,
                            'lines': func_lines
                        })
                
                # Check class sizes
                for class_name, class_node in get_all_classes(tree):
                    methods = [n for n in ast.walk(class_node) 
                              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    if len(methods) > 7:
                        large_classes.append({
                            'module': module,
                            'class': class_name,
                            'methods': len(methods)
                        })
        
        # Sort by line count
        long_files = [
            {'module': mod, 'lines': lines}
            for mod, lines in sorted(file_lines.items(), key=lambda x: -x[1])
        ]
        
        return {
            'file_lines': file_lines,
            'long_files': long_files,
            'long_functions': sorted(long_functions, key=lambda x: -x['lines']),
            'large_classes': sorted(large_classes, key=lambda x: -x['methods']),
        }
