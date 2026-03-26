"""JSON reporter for machine-readable output."""

import json
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import BaseReporter


class JSONReporter(BaseReporter):
    """
    Generate JSON reports for CI/CD integration.
    
    Outputs complete analysis results in JSON format.
    """
    
    def __init__(self, indent: int = 2):
        """
        Initialize reporter.
        
        Args:
            indent: JSON indentation level (None for compact)
        """
        self.indent = indent
    
    @property
    def format_name(self) -> str:
        return "json"
    
    def report(self, results: dict[str, Any]) -> str:
        """Generate JSON report."""
        # Ensure all sets are converted to lists for JSON serialization
        serializable = self._make_serializable(results)
        return json.dumps(serializable, indent=self.indent)
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if isinstance(obj, set):
            return sorted(obj)
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj
