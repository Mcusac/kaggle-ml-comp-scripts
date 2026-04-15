"""Base reporter class for all code health reporters."""

from abc import ABC, abstractmethod
from typing import Any


class BaseReporter(ABC):
    """
    Abstract base class for all code health reporters.
    
    Reporters transform analysis results into human-readable or machine-readable formats.
    """
    
    @abstractmethod
    def report(self, results: dict[str, Any]) -> str:
        """
        Generate report from analysis results.
        
        Args:
            results: Dictionary containing analysis results from analyzers
            
        Returns:
            Formatted report as string
        """
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the format name of this reporter (e.g., 'console', 'json')."""
        pass
