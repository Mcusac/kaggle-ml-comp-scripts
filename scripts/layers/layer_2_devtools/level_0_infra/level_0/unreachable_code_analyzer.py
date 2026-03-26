"""Unreachable code analyzer for dead code detection."""

import ast
from typing import Any, Dict, List


class UnreachableCodeAnalyzer:
    """Analyzes and detects unreachable code in Python files."""
    
    def find_unreachable_code(self, tree: ast.AST, module: str) -> List[Dict[str, Any]]:
        """Find code after return/raise statements."""
        unreachable = []
        
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            
            # Check each function body
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, (ast.Return, ast.Raise)):
                    # Check if there's code after this
                    if i < len(node.body) - 1:
                        next_stmt = node.body[i + 1]
                        unreachable.append({
                            'module': module,
                            'function': node.name,
                            'line': next_stmt.lineno,
                            'reason': f'Code after {stmt.__class__.__name__.lower()}'
                        })
        
        return unreachable
