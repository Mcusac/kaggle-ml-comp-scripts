"""Discover contest implementation modules and run import validation."""

from pathlib import Path
from typing import Optional

from layers.layer_2_devtools.level_0_infra.level_0 import (
    ErrorClassifier,
    ModuleDiscoverer,
)
from layers.layer_2_devtools.level_0_infra.level_0 import ErrorType
from layers.layer_2_devtools.level_0_infra.level_0 import DiscoveryConfig
from layers.layer_2_devtools.level_0_infra.level_1 import ImportTester


def discover_contest_modules(scripts_root: Path) -> list[str]:
    """Discover full module paths under contest/implementations/."""
    impl_dir = scripts_root / "contest" / "implementations"
    if not impl_dir.exists():
        return []

    modules: list[str] = []
    for contest_dir in impl_dir.iterdir():
        if not contest_dir.is_dir() or contest_dir.name.startswith("_"):
            continue
        base_module = f"contest.implementations.{contest_dir.name}"
        modules.extend(_walk_contest_directory(contest_dir, base_module))

    return sorted(set(modules))


def _walk_contest_directory(path: Path, base_module: str) -> list[str]:
    modules: list[str] = []
    for item in sorted(path.iterdir()):
        if _should_skip_item(item):
            continue
        if item.is_file() and item.suffix == ".py":
            module_name = _get_module_name_from_file(item, base_module)
            if module_name:
                modules.append(module_name)
        elif item.is_dir() and _is_python_package(item):
            new_module = f"{base_module}.{item.name}" if base_module else item.name
            modules.extend(_walk_contest_directory(item, new_module))
    return modules


def _should_skip_item(item: Path) -> bool:
    return (
        item.name.startswith("test_")
        or item.name == "__pycache__"
        or item.name.startswith(".")
        or item.name.startswith("_")
    )


def _get_module_name_from_file(file_path: Path, base_module: str) -> Optional[str]:
    if file_path.stem == "__init__":
        return base_module if base_module else None
    return f"{base_module}.{file_path.stem}" if base_module else file_path.stem


def _is_python_package(directory: Path) -> bool:
    if directory.name.startswith("_") or directory.name.startswith("."):
        return False
    init_file = directory / "__init__.py"
    if init_file.exists():
        return True
    return any(f.suffix == ".py" for f in directory.iterdir() if f.is_file())


def print_validation_results(results, verbose: bool = False) -> tuple[int, int]:
    """Print validation results; return (structural_error_count, dependency_count)."""
    passed = [r for r in results if r.passed]
    structural = [
        r for r in results if r.error_info and r.error_info.error_type == ErrorType.STRUCTURAL
    ]
    dependency = [
        r for r in results if r.error_info and r.error_info.error_type == ErrorType.DEPENDENCY
    ]
    other = [
        r for r in results if r.error_info and r.error_info.error_type == ErrorType.OTHER
    ]

    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()

    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Structural errors: {len(structural) + len(other)}")
    print(f"📦 Missing dependencies: {len(dependency)}")
    print()

    if structural or other:
        print("=" * 80)
        print("STRUCTURAL ERRORS (MUST FIX)")
        print("=" * 80)
        all_errors = structural + other
        for result in all_errors:
            print(f"\n❌ {result.name}")
            print(f"   Error: {result.error_info.error_message.split(chr(10))[0]}")
            if verbose:
                print(f"   Full error:\n{result.error_info.error_message}")
        print()

    if dependency and verbose:
        print("=" * 80)
        print("MISSING DEPENDENCIES (Optional - install if needed)")
        print("=" * 80)
        for result in dependency:
            print(f"\n📦 {result.name}")
            if result.error_info.missing_dependency:
                print(f"   Missing: {result.error_info.missing_dependency}")
            print(f"   Error: {result.error_info.error_message.split(chr(10))[0]}")
        print()

    return len(structural) + len(other), len(dependency)


def run_pre_upload_validation(scripts_root: Path, verbose: bool) -> int:
    """Run discovery + ImportTester over contest modules. Return exit code."""
    scripts_root = scripts_root.resolve()
    if not scripts_root.exists():
        print(f"❌ Error: Scripts directory not found: {scripts_root}")
        return 1

    print("=" * 80)
    print("PRE-UPLOAD VALIDATION")
    print("=" * 80)
    print(f"Scripts directory: {scripts_root}")
    print()

    print("Discovering contest implementation modules...")
    modules = discover_contest_modules(scripts_root)
    print(f"Found {len(modules)} modules to validate\n")

    config = DiscoveryConfig(scripts_dir=scripts_root)
    discoverer = ModuleDiscoverer(config)
    classifier = ErrorClassifier(discoverer.codebase_packages)
    tester = ImportTester(classifier, verbose=verbose)

    for i, module_name in enumerate(modules, 1):
        if verbose:
            print(f"[{i}/{len(modules)}] Validating {module_name}...")
        tester.test_module_import(module_name)

    structural_count, _dep = print_validation_results(tester.results, verbose=verbose)

    if structural_count > 0:
        print("=" * 80)
        print("❌ VALIDATION FAILED")
        print(
            f"Found {structural_count} structural error(s) that must be fixed before upload."
        )
        print("=" * 80)
        return 1

    print("=" * 80)
    print("✅ VALIDATION PASSED")
    print("All modules imported successfully. Safe to upload!")
    print("=" * 80)
    return 0
