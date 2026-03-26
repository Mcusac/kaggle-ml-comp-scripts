"""Type annotation checker for detecting missing type imports."""

import ast

from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import (
    BaseAnalyzer,
    collect_python_files,
    file_to_module,
    parse_file,
)


# Common type annotations that should be imported from typing
TYPE_ANNOTATIONS = {
    'Any', 'Dict', 'List', 'Tuple', 'Optional', 'Union',
    'Callable', 'TypeVar', 'Generic', 'Protocol', 'Type',
    'Set', 'FrozenSet', 'Iterable', 'Iterator', 'Sequence',
    'Mapping', 'MutableMapping', 'OrderedDict', 'DefaultDict',
    'Counter', 'Deque', 'ChainMap', 'Awaitable', 'Coroutine',
    'AsyncIterable', 'AsyncIterator', 'Literal', 'TypedDict',
    'Final', 'ClassVar', 'cast', 'overload', 'no_type_check'
}


class TypeAnnotationChecker(BaseAnalyzer):
    """
    Check for missing type annotation imports.
    
    Detects usage of type annotations (Any, Dict, List, etc.) that are not
    imported from the typing module, which causes NameError at runtime.
    """
    
    @property
    def name(self) -> str:
        return "type_annotations"
    
    def analyze(self) -> dict[str, Any]:
        """Check all Python files for missing type annotation imports."""
        files = collect_python_files(self.root)
        
        missing_imports = []
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            # Parse file
            tree = parse_file(file_path)
            if not tree:
                continue
            
            # Get all imports from typing
            typing_imports = self._get_typing_imports(tree)
            
            # Find all type annotations used in the file
            used_types = self._find_used_type_annotations(tree)
            
            # Check which used types are not imported
            for type_name, line_num in used_types:
                if type_name not in typing_imports:
                    missing_imports.append({
                        'file': module,
                        'line': line_num,
                        'type': type_name,
                        'suggested_import': f"from typing import {type_name}"
                    })
        
        return {
            'missing_imports': missing_imports,
            'total_missing': len(missing_imports)
        }
    
    def _get_typing_imports(self, tree: ast.AST) -> set[str]:
        """Extract all type annotations imported from typing module."""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'typing':
                    for alias in node.names:
                        imports.add(alias.asname or alias.name)
            elif isinstance(node, ast.Import):
                # Handle 'import typing' case
                for alias in node.names:
                    if alias.name == 'typing':
                        # If typing is imported as a module, we can't detect individual types
                        # But we can check for typing.Any, typing.Dict, etc.
                        # For now, we'll mark common ones as available
                        pass
        
        return imports
    
    def _find_used_type_annotations(self, tree: ast.AST) -> list[tuple[str, int]]:
        """Find all type annotations used in the AST."""
        used_types = []
        
        for node in ast.walk(tree):
            # Check function annotations
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Return type annotation
                if node.returns:
                    used_types.extend(self._extract_types_from_annotation(node.returns, node.lineno))
                
                # Parameter type annotations
                for arg in node.args.args:
                    if arg.annotation:
                        used_types.extend(self._extract_types_from_annotation(arg.annotation, node.lineno))
                
                # Keyword-only arguments
                for arg in node.args.kwonlyargs:
                    if arg.annotation:
                        used_types.extend(self._extract_types_from_annotation(arg.annotation, node.lineno))
            
            # Check variable annotations
            elif isinstance(node, ast.AnnAssign):
                if node.annotation:
                    used_types.extend(self._extract_types_from_annotation(node.annotation, node.lineno))
            
            # Check class attribute annotations
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.AnnAssign):
                        if item.annotation:
                            used_types.extend(self._extract_types_from_annotation(item.annotation, item.lineno))
        
        return used_types
    
    def _extract_types_from_annotation(self, annotation: ast.AST, line_num: int) -> list[tuple[str, int]]:
        """Extract type names from an annotation AST node."""
        types = []
        
        if isinstance(annotation, ast.Name):
            # Simple type like 'Any', 'Dict', etc.
            if annotation.id in TYPE_ANNOTATIONS:
                types.append((annotation.id, line_num))
        
        elif isinstance(annotation, ast.Subscript):
            # Generic type like 'Dict[str, int]', 'List[str]', etc.
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id in TYPE_ANNOTATIONS:
                    types.append((annotation.value.id, line_num))
            elif isinstance(annotation.value, ast.Attribute):
                # Handle typing.Dict, typing.List, etc.
                if isinstance(annotation.value.value, ast.Name) and annotation.value.value.id == 'typing':
                    types.append((annotation.value.attr, line_num))
        
        elif isinstance(annotation, ast.Attribute):
            # Handle typing.Any, typing.Dict, etc.
            if isinstance(annotation.value, ast.Name) and annotation.value.id == 'typing':
                if annotation.attr in TYPE_ANNOTATIONS:
                    types.append((annotation.attr, line_num))
        
        elif isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            # Union type like 'str | int' (Python 3.10+)
            # For older Python, this would be Union[str, int]
            # We'll check both operands
            types.extend(self._extract_types_from_annotation(annotation.left, line_num))
            types.extend(self._extract_types_from_annotation(annotation.right, line_num))
        
        return types
