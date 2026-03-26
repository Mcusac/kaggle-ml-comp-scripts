"""Import tester for validating module imports."""

import importlib
import traceback
from dataclasses import dataclass
from typing import Callable

from layers.layer_2_devtools.level_0_infra.level_0 import ErrorClassifier, ErrorInfo, ErrorType


@dataclass
class TestResult:
    """Result of an import test."""
    name: str
    passed: bool
    error_info: ErrorInfo | None = None


class ImportTester:
    """
    Test module imports and classify failures.
    
    Separates dependency errors from structural errors.
    """
    
    def __init__(self, classifier: ErrorClassifier, verbose: bool = False):
        """
        Initialize tester.
        
        Args:
            classifier: Error classifier
            verbose: Whether to print verbose output
        """
        self.classifier = classifier
        self.verbose = verbose
        self.results: list[TestResult] = []
    
    def test_import(self, name: str, import_func: Callable) -> TestResult:
        """
        Test an import.
        
        Args:
            name: Name of test
            import_func: Function to call for import
            
        Returns:
            TestResult
        """
        try:
            import_func()
            result = TestResult(name=name, passed=True)
            self._print(f"✅ [PASS] {name}")
        except (ModuleNotFoundError, ImportError) as e:
            error_info = self.classifier.classify(name, e)
            result = TestResult(name=name, passed=False, error_info=error_info)
            
            if error_info.error_type == ErrorType.DEPENDENCY:
                self._print(f"📦 [DEPS] {name}: Missing '{error_info.missing_dependency}'")
            else:
                self._print(f"❌ [FAIL] {name}: {error_info.error_message}")
                if self.verbose:
                    traceback.print_exc()
        except Exception as e:
            error_info = self.classifier.classify(name, e)
            result = TestResult(name=name, passed=False, error_info=error_info)
            self._print(f"❌ [FAIL] {name}: {error_info.error_message}")
            if self.verbose:
                traceback.print_exc()
        
        self.results.append(result)
        return result
    
    def test_module_import(self, module_name: str) -> TestResult:
        """
        Test importing a module.
        
        Args:
            module_name: Full module name
            
        Returns:
            TestResult
        """
        def import_module():
            importlib.import_module(module_name)
        
        return self.test_import(module_name, import_module)
    
    def test_module_attributes(self, module_name: str, attributes: list[str]) -> list[TestResult]:
        """
        Test that a module has specific attributes.
        
        Args:
            module_name: Module name
            attributes: List of attribute names to check
            
        Returns:
            List of TestResults
        """
        results = []
        
        try:
            module = importlib.import_module(module_name)
            for attr in attributes:
                attr_name = f"{module_name}.{attr}"
                if hasattr(module, attr):
                    def get_attr(m=module, a=attr):
                        return getattr(m, a)
                    result = self.test_import(attr_name, get_attr)
                else:
                    error_info = ErrorInfo(
                        error_type=ErrorType.STRUCTURAL,
                        module_name=attr_name,
                        error_message=f"Attribute '{attr}' not found"
                    )
                    result = TestResult(name=attr_name, passed=False, error_info=error_info)
                    self._print(f"❌ [FAIL] {attr_name}: Attribute not found")
                    self.results.append(result)
                
                results.append(result)
        
        except (ModuleNotFoundError, ImportError) as e:
            # If module can't be imported, all attributes fail
            error_info = self.classifier.classify(module_name, e)
            for attr in attributes:
                attr_name = f"{module_name}.{attr}"
                result = TestResult(name=attr_name, passed=False, error_info=error_info)
                self.results.append(result)
                results.append(result)
                
                if error_info.error_type == ErrorType.DEPENDENCY:
                    self._print(f"📦 [DEPS] {attr_name}: Missing '{error_info.missing_dependency}'")
                else:
                    self._print(f"❌ [FAIL] {attr_name}: {error_info.error_message}")
        
        except Exception as e:
            # Other errors
            error_info = self.classifier.classify(module_name, e)
            for attr in attributes:
                attr_name = f"{module_name}.{attr}"
                result = TestResult(name=attr_name, passed=False, error_info=error_info)
                self.results.append(result)
                results.append(result)
                self._print(f"❌ [FAIL] {attr_name}: {error_info.error_message}")
        
        return results
    
    def _print(self, message: str):
        """Print message if not in quiet mode."""
        print(message)
    
    def get_summary(self) -> dict[str, int]:
        """
        Get test summary.
        
        Returns:
            Dictionary with counts
        """
        passed = sum(1 for r in self.results if r.passed)
        dependency = sum(1 for r in self.results if r.error_info and r.error_info.error_type == ErrorType.DEPENDENCY)
        structural = sum(1 for r in self.results if r.error_info and r.error_info.error_type == ErrorType.STRUCTURAL)
        other = sum(1 for r in self.results if r.error_info and r.error_info.error_type == ErrorType.OTHER)
        
        return {
            'passed': passed,
            'dependency_errors': dependency,
            'structural_errors': structural,
            'other_errors': other,
            'total': len(self.results)
        }
