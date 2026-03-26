"""Code duplication detector."""

from pathlib import Path
from typing import Any
import hashlib
import re

from layers.layer_2_devtools.level_0_infra.level_0 import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.io import text_file as file_utils
from layers.layer_2_devtools.level_0_infra.level_0 import collect_python_files, file_to_module


class DuplicationDetector(BaseAnalyzer):
    """
    Detect duplicated code blocks.
    
    Uses token-based hashing to find similar code segments.
    Filters false positives (imports, boilerplate, standard patterns).
    """
    
    def __init__(self, root: Path, min_lines: int = 6, filter_false_positives: bool = True):
        """
        Initialize detector.
        
        Args:
            root: Root directory
            min_lines: Minimum lines to consider for duplication
            filter_false_positives: Whether to filter common false positives (default: True)
        """
        super().__init__(root)
        self.min_lines = min_lines
        self.filter_false_positives = filter_false_positives
    
    @property
    def name(self) -> str:
        return "duplication"
    
    def _is_import_block(self, normalized: list[str]) -> bool:
        """
        Check if block is import-only.
        
        Args:
            normalized: List of normalized lines
            
        Returns:
            True if all lines are imports
        """
        if not normalized:
            return False
        
        import_patterns = [
            r'^import\s+',
            r'^from\s+\S+\s+import\s+',
            r'^from\s+\.',
        ]
        
        for line in normalized:
            is_import = any(re.match(pattern, line) for pattern in import_patterns)
            if not is_import:
                return False
        
        return True
    
    def _is_boilerplate_block(self, normalized: list[str]) -> bool:
        """
        Check if block is common boilerplate.
        
        Args:
            normalized: List of normalized lines
            
        Returns:
            True if block is common boilerplate
        """
        if not normalized:
            return False
        
        # Single-line boilerplate patterns
        boilerplate_patterns = [
            r'^logger\s*=\s*logging\.getLogger\(__name__\)$',
            r'^logger\s*=\s*logging\.getLogger\(["\']',
        ]
        
        # Check if all lines match boilerplate patterns
        if len(normalized) == 1:
            line = normalized[0]
            return any(re.match(pattern, line) for pattern in boilerplate_patterns)
        
        # Check for standard docstring patterns (triple quotes)
        if len(normalized) <= 3:
            all_docstring = all(
                line.startswith('"""') or line.endswith('"""') or 
                line.startswith("'''") or line.endswith("'''") or
                line.strip() == ''
                for line in normalized
            )
            if all_docstring:
                return True
        
        return False
    
    def _is_overlapping_window(self, file1: str, line1: int, file2: str, line2: int) -> bool:
        """
        Check if two blocks are overlapping windows in the same file.
        
        Args:
            file1: First file module
            line1: First line number
            file2: Second file module
            line2: Second line number
            
        Returns:
            True if same file and lines are within window size
        """
        if file1 != file2:
            return False
        
        # Check if lines are within min_lines of each other (overlapping windows)
        return abs(line1 - line2) < self.min_lines
    
    def _should_filter_block(self, normalized: list[str], original_lines: list[str]) -> bool:
        """
        Determine if block should be filtered as false positive.
        
        Args:
            normalized: Normalized lines (stripped, no comments)
            original_lines: Original lines from file
            
        Returns:
            True if block should be filtered
        """
        if not self.filter_false_positives:
            return False
        
        # Filter import-only blocks
        if self._is_import_block(normalized):
            return True
        
        # Filter boilerplate blocks
        if self._is_boilerplate_block(normalized):
            return True
        
        return False
    
    def analyze(self) -> dict[str, Any]:
        """Detect code duplication."""
        files = collect_python_files(self.root)
        
        # Build hash map of code blocks
        block_hashes: dict[str, list[tuple[str, int]]] = {}
        
        for file_path in files:
            module = file_to_module(file_path, self.root)
            if not module:
                continue
            
            content = file_utils.read_file_safe(file_path)
            if not content:
                continue
            
            lines = content.splitlines()
            
            # Generate hashes for sliding windows
            for i in range(len(lines) - self.min_lines + 1):
                block = lines[i:i + self.min_lines]
                
                # Normalize: strip whitespace, skip empty/comment-only blocks
                normalized = [line.strip() for line in block if line.strip() and not line.strip().startswith('#')]
                
                if len(normalized) < self.min_lines:
                    continue
                
                # Filter false positives
                if self._should_filter_block(normalized, block):
                    continue
                
                # Hash the normalized block
                block_hash = hashlib.md5('\n'.join(normalized).encode()).hexdigest()
                block_hashes.setdefault(block_hash, []).append((module, i + 1))
        
        # Find duplicates and calculate frequency
        duplicate_blocks = []
        block_frequencies: dict[str, int] = {}
        
        for block_hash, locations in block_hashes.items():
            if len(locations) > 1:
                frequency = len(locations)
                block_frequencies[block_hash] = frequency
                
                # Multiple locations with same hash = duplication
                # Filter overlapping windows in same file
                for i in range(len(locations) - 1):
                    file1, line1 = locations[i]
                    file2, line2 = locations[i + 1]
                    
                    # Skip overlapping windows in same file
                    if self._is_overlapping_window(file1, line1, file2, line2):
                        continue
                    
                    duplicate_blocks.append({
                        'file1': file1,
                        'line1': line1,
                        'file2': file2,
                        'line2': line2,
                        'lines': self.min_lines,
                        'hash': block_hash[:8],
                        'frequency': frequency
                    })
        
        return {
            'duplicate_blocks': duplicate_blocks,
            'total_duplicates': len(duplicate_blocks),
            'block_frequencies': {k[:8]: v for k, v in block_frequencies.items() if v > 1},
        }
