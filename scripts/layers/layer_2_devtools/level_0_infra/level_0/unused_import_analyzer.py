"""Unused import analyzer for dead code detection."""

import ast
from typing import Set


class UnusedImportAnalyzer:
    """Analyzes and detects unused imports in Python code."""
    
    def collect_imports(self, tree: ast.AST) -> Set[str]:
        """
        Collect all imported names from AST.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            Set of imported names
        """
        imports: Set[str] = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split('.')[0]
                    imports.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != '*':
                        name = alias.asname or alias.name
                        imports.add(name)
        
        return imports
    
    def extract_all_exports(self, tree: ast.AST) -> Set[str]:
        """
        Extract names from __all__ assignments (for __init__.py re-exports).
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            Set of names in __all__
        """
        __all__ = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        # Extract names from __all__ list
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    __all__.add(elt.value)
                                elif isinstance(elt, ast.Str):  # Python < 3.8
                                    __all__.add(elt.s)
        
        return __all__
    
    def collect_used_names(self, tree: ast.AST) -> Set[str]:
        """
        Collect all used names from AST, including type annotations.
        
        Args:
            tree: AST tree to analyze
            
        Returns:
            Set of used names
        """
        used_names: Set[str] = set()
        
        # Collect basic name usages
        used_names.update(self._collect_basic_name_usages(tree))
        
        # Collect names from type annotations
        used_names.update(self._collect_type_annotation_names(tree))
        
        return used_names
    
    def _collect_basic_name_usages(self, tree: ast.AST) -> Set[str]:
        """Collect names from basic AST nodes (Name, Attribute)."""
        used_names: Set[str] = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Get the root name
                curr = node
                while isinstance(curr, ast.Attribute):
                    curr = curr.value
                if isinstance(curr, ast.Name):
                    used_names.add(curr.id)
        
        return used_names
    
    def _collect_type_annotation_names(self, tree: ast.AST) -> Set[str]:
        """Collect names used in type annotations."""
        used_names: Set[str] = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Return type annotation
                if node.returns:
                    used_names.update(self._extract_names_from_annotation(node.returns))
                # Parameter annotations
                used_names.update(self._collect_function_param_annotations(node))
            elif isinstance(node, ast.AnnAssign):
                # Variable annotations
                if node.annotation:
                    used_names.update(self._extract_names_from_annotation(node.annotation))
        
        return used_names
    
    def _collect_function_param_annotations(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> Set[str]:
        """Collect names from function parameter annotations."""
        used_names: Set[str] = set()
        
        for arg in func_node.args.args:
            if arg.annotation:
                used_names.update(self._extract_names_from_annotation(arg.annotation))
        
        for arg in func_node.args.kwonlyargs:
            if arg.annotation:
                used_names.update(self._extract_names_from_annotation(arg.annotation))
        
        return used_names
    
    def _extract_names_from_annotation(self, annotation: ast.AST) -> Set[str]:
        """Extract all name identifiers from a type annotation."""
        names = set()
        
        if isinstance(annotation, ast.Name):
            names.add(annotation.id)
        elif isinstance(annotation, ast.Subscript):
            # Handle generic types like Optional[str], Dict[str, int]
            if isinstance(annotation.value, ast.Name):
                names.add(annotation.value.id)
            # Recursively check slice (the type parameters)
            if isinstance(annotation.slice, ast.Tuple):
                for elt in annotation.slice.elts:
                    names.update(self._extract_names_from_annotation(elt))
            elif annotation.slice:
                names.update(self._extract_names_from_annotation(annotation.slice))
        elif isinstance(annotation, ast.Attribute):
            # Handle typing.Optional, typing.Dict, etc.
            if isinstance(annotation.value, ast.Name):
                names.add(annotation.value.id)
            names.add(annotation.attr)
        elif isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            # Union type like 'str | int' (Python 3.10+)
            names.update(self._extract_names_from_annotation(annotation.left))
            names.update(self._extract_names_from_annotation(annotation.right))
        
        return names
    
    def get_type_checking_imports(self, tree: ast.AST) -> Set[str]:
        """
        Get imports that are within TYPE_CHECKING blocks.
        
        These imports are only used for type checking and should be
        considered as used even if they don't appear in runtime code.
        """
        if not self._has_type_checking_import(tree):
            return set()
        
        return self._extract_type_checking_block_imports(tree)
    
    def _has_type_checking_import(self, tree: ast.AST) -> bool:
        """Check if TYPE_CHECKING is imported from typing."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'typing':
                    for alias in node.names:
                        if alias.name == 'TYPE_CHECKING':
                            return True
        return False
    
    def _extract_type_checking_block_imports(self, tree: ast.AST) -> Set[str]:
        """Extract imports from TYPE_CHECKING if blocks."""
        type_checking_imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if self._is_type_checking_block(node):
                    type_checking_imports.update(self._collect_imports_from_node(node))
        
        return type_checking_imports
    
    def _is_type_checking_block(self, if_node: ast.If) -> bool:
        """Check if an if statement is a TYPE_CHECKING block."""
        return isinstance(if_node.test, ast.Name) and if_node.test.id == 'TYPE_CHECKING'
    
    def _collect_imports_from_node(self, node: ast.AST) -> Set[str]:
        """Collect all import names from a node and its children."""
        imports = set()
        
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    name = alias.asname or alias.name.split('.')[0]
                    imports.add(name)
            elif isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    if alias.name != '*':
                        name = alias.asname or alias.name
                        imports.add(name)
        
        return imports
    
    def find_unused_imports(self, tree: ast.AST, module: str) -> list[str]:
        """Find imports that are never used."""
        imports = self.collect_imports(tree)
        __all__ = self.extract_all_exports(tree)
        used_names = self.collect_used_names(tree)
        
        # Names in __all__ are considered used (re-exports)
        used_names.update(__all__)
        
        # Handle TYPE_CHECKING imports
        type_checking_imports = self.get_type_checking_imports(tree)
        if type_checking_imports:
            used_names.update(type_checking_imports)
        
        # Find unused
        unused = imports - used_names
        return sorted(unused)
