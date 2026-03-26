"""Cyclomatic complexity analyzer."""

import ast

from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import (
    BaseAnalyzer,
    collect_python_files,
    file_to_module,
    get_all_classes,
    get_all_functions,
    get_function_complexity,
    parse_file,
)


class ComplexityAnalyzer(BaseAnalyzer):
    """
    Analyze cyclomatic complexity of functions and classes.
    
    Uses McCabe complexity metric.
    """
    
    @property
    def name(self) -> str:
        return "complexity"
    
    def analyze(self) -> dict[str, Any]:
        """Analyze complexity metrics."""
        files = collect_python_files(self.root)
        
        function_complexity: list[dict[str, Any]] = []
        class_complexity: list[dict[str, Any]] = []
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            tree = parse_file(file_path)
            if not tree:
                continue
            
            # Analyze function complexity
            for func_name, func_node in get_all_functions(tree):
                complexity = get_function_complexity(func_node)
                function_complexity.append({
                    'module': module,
                    'name': func_name,
                    'complexity': complexity,
                    'line': func_node.lineno
                })
            
            # Analyze class complexity (sum of method complexities)
            for class_name, class_node in get_all_classes(tree):
                total_complexity = 0
                method_count = 0
                
                for node in class_node.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_complexity += get_function_complexity(node)
                        method_count += 1
                
                if method_count > 0:
                    class_complexity.append({
                        'module': module,
                        'name': class_name,
                        'complexity': total_complexity,
                        'methods': method_count,
                        'avg_complexity': round(total_complexity / method_count, 2),
                        'line': class_node.lineno
                    })
        
        return {
            'functions': sorted(function_complexity, key=lambda x: -x['complexity']),
            'classes': sorted(class_complexity, key=lambda x: -x['complexity']),
        }
