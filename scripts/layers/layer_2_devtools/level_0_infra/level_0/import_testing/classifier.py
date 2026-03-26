"""Error classification for import testing."""

import re
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    """Type of import error."""
    DEPENDENCY = "dependency"  # Missing external dependency
    STRUCTURAL = "structural"  # Internal structural issue
    OTHER = "other"  # Other unexpected error


@dataclass
class ErrorInfo:
    """Information about an import error."""
    error_type: ErrorType
    module_name: str
    error_message: str
    missing_dependency: str | None = None


class ErrorClassifier:
    """
    Classify import errors as dependency vs structural issues.
    
    Dependency errors: Missing external packages (need pip install).
    Structural errors: Internal code issues (need fixing).
    """
    
    def __init__(self, codebase_packages: set[str]):
        """
        Initialize classifier.
        
        Args:
            codebase_packages: Set of internal package names
        """
        self.codebase_packages = codebase_packages
    
    def classify(self, module_name: str, error: Exception) -> ErrorInfo:
        """
        Classify an import error.
        
        Args:
            module_name: Name of module that failed to import
            error: Exception that was raised
            
        Returns:
            ErrorInfo with classification
        """
        error_msg = str(error)
        error_lower = error_msg.lower()
        
        # Check if it's a "No module named" error
        if "no module named" in error_lower:
            match = re.search(r"no module named ['\"]([^'\"]+)['\"]", error_lower)
            if match:
                missing_module = match.group(1)
                missing_base = missing_module.split('.')[0]
                
                if missing_base not in self.codebase_packages:
                    # External dependency
                    return ErrorInfo(
                        error_type=ErrorType.DEPENDENCY,
                        module_name=module_name,
                        error_message=error_msg,
                        missing_dependency=missing_module
                    )
                else:
                    # Codebase module - structural error
                    return ErrorInfo(
                        error_type=ErrorType.STRUCTURAL,
                        module_name=module_name,
                        error_message=error_msg
                    )
        
        # ImportError with "cannot import" - usually structural
        if "cannot import" in error_lower or "cannot import name" in error_lower:
            return ErrorInfo(
                error_type=ErrorType.STRUCTURAL,
                module_name=module_name,
                error_message=error_msg
            )
        
        # Other errors
        return ErrorInfo(
            error_type=ErrorType.OTHER,
            module_name=module_name,
            error_message=error_msg
        )
