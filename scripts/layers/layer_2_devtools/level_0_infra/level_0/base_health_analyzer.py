"""Base analyzer class for all code health analyzers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseAnalyzer(ABC):
    """
    Abstract base class for all code health analyzers.
    
    Implements the Template Method pattern for consistent analyzer interface.
    Each analyzer must implement analyze() to return analysis results.
    """
    
    def __init__(self, root: Path):
        """
        Initialize analyzer.
        
        Args:
            root: Root directory to analyze
        """
        self.root = root.resolve()
        if not self.root.is_dir():
            raise ValueError(f"Root is not a directory: {self.root}")
    
    @abstractmethod
    def analyze(self) -> dict[str, Any]:
        """
        Run analysis on the codebase.
        
        Returns:
            Dictionary containing analysis results.
            Format is analyzer-specific but should be JSON-serializable.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this analyzer."""
        pass
