"""Test reporter for import testing results."""

from typing import List

from layers.layer_2_devtools.level_0_infra.level_0 import ErrorType
from layers.layer_2_devtools.level_0_infra.level_1 import TestResult


class TestReporter:
    """
    Generate test reports and summaries.
    
    Provides formatted output for test results.
    """
    
    def __init__(self, results: List[TestResult]):
        """
        Initialize reporter.
        
        Args:
            results: List of test results
        """
        self.results = results
    
    def print_summary(self) -> int:
        """
        Print test summary.
        
        Returns:
            Exit code (0 if all passed, 1 if structural errors)
        """
        passed = [r for r in self.results if r.passed]
        dependency_errors = [r for r in self.results if r.error_info and r.error_info.error_type == ErrorType.DEPENDENCY]
        structural_errors = [r for r in self.results if r.error_info and r.error_info.error_type == ErrorType.STRUCTURAL]
        other_errors = [r for r in self.results if r.error_info and r.error_info.error_type == ErrorType.OTHER]
        
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ [PASS] Passed: {len(passed)}")
        print(f"📦 [DEPS] Missing dependencies: {len(dependency_errors)}")
        print(f"❌ [FAIL] Structural errors: {len(structural_errors) + len(other_errors)}")
        print()
        
        # Show missing dependencies summary
        if dependency_errors:
            print("MISSING DEPENDENCIES (Install these to use the codebase):")
            print("-" * 80)
            
            dep_groups = {}
            for result in dependency_errors:
                dep = result.error_info.missing_dependency
                if dep not in dep_groups:
                    dep_groups[dep] = []
                dep_groups[dep].append(result.name)
            
            for dep, modules in sorted(dep_groups.items()):
                print(f"  {dep}: {len(modules)} modules need this")
            
            print()
            print("To install dependencies, run:")
            print("  pip install " + " ".join(sorted(dep_groups.keys())))
            print()
            print("Or if you have a requirements.txt:")
            print("  pip install -r requirements.txt")
            print()
        
        # Show structural errors
        if structural_errors or other_errors:
            print("STRUCTURAL IMPORT ERRORS (These need to be fixed):")
            print("-" * 80)
            all_errors = structural_errors + other_errors
            for result in all_errors[:20]:
                print(f"  {result.name}: {result.error_info.error_message}")
            if len(all_errors) > 20:
                print(f"  ... and {len(all_errors) - 20} more failures")
            print()
            return 1
        else:
            if dependency_errors:
                print("✅ All structural imports successful!")
                print(f"⚠️  {len(dependency_errors)} modules need dependencies installed")
                print("   Install dependencies to use these modules.")
            else:
                print("🎉 All imports successful!")
            return 0
