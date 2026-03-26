"""Dead code finder."""

from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import (
    BaseAnalyzer,
    collect_python_files,
    file_to_module,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file
from layers.layer_2_devtools.level_0_infra.level_0.unreachable_code_analyzer import UnreachableCodeAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.unused_import_analyzer import UnusedImportAnalyzer


class DeadCodeFinder(BaseAnalyzer):
    """
    Find potentially dead code.
    
    Detects:
    - Unused imports
    - Unreachable code after return/raise
    
    Uses composition with specialized analyzers for each type of dead code.
    """
    
    def __init__(self, root):
        """Initialize dead code finder with specialized analyzers."""
        super().__init__(root)
        self.import_analyzer = UnusedImportAnalyzer()
        self.unreachable_analyzer = UnreachableCodeAnalyzer()
    
    @property
    def name(self) -> str:
        return "dead_code"
    
    def analyze(self) -> dict[str, Any]:
        """Find dead code."""
        files = collect_python_files(self.root)
        
        unused_imports: list[dict[str, Any]] = []
        unreachable_code: list[dict[str, Any]] = []
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            tree = parse_file(file_path)
            if not tree:
                continue
            
            # Find unused imports
            unused = self.import_analyzer.find_unused_imports(tree, module)
            if unused:
                unused_imports.append({
                    'module': module,
                    'names': unused
                })
            
            # Find unreachable code
            unreachable = self.unreachable_analyzer.find_unreachable_code(tree, module)
            unreachable_code.extend(unreachable)
        
        return {
            'unused_imports': unused_imports,
            'unreachable_code': unreachable_code,
            'total_unused_imports': sum(len(u['names']) for u in unused_imports),
            'total_unreachable_blocks': len(unreachable_code),
        }
    
