"""Public API: import-test suite (moved from dev/tests for thin entrypoints)."""

import importlib
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok
from layers.layer_2_devtools.level_0_infra.level_0.import_testing.classifier import ErrorClassifier
from layers.layer_2_devtools.level_0_infra.level_0.import_testing.discoverer import DiscoveryConfig
from layers.layer_2_devtools.level_0_infra.level_0.import_testing.discoverer import ModuleDiscoverer
from layers.layer_2_devtools.level_0_infra.level_1.tester import ImportTester
from layers.layer_2_devtools.level_0_infra.level_2.reporter import TestReporter


def run_import_test_suite_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Run the comprehensive import test suite.

    Config: ``scripts_root`` (Path), ``verbose`` (bool).
    """
    try:
        scripts_dir = Path(config["scripts_root"])
        verbose = bool(config.get("verbose", False))

        print("=" * 80)
        print("IMPORT TEST SUITE - Kaggle ML Competition Scripts")
        print("=" * 80)
        print()

        print("Discovering Python modules...")
        print("-" * 80)

        discovery_cfg = DiscoveryConfig(scripts_dir=scripts_dir)
        discoverer = ModuleDiscoverer(discovery_cfg)

        print(f"Detected codebase packages: {', '.join(sorted(discoverer.codebase_packages))}")

        all_modules = discoverer.get_all_modules()
        for package, modules in all_modules.items():
            print(f"Found {len(modules)} modules in {package}")

        print()

        classifier = ErrorClassifier(discoverer.codebase_packages)
        tester = ImportTester(classifier, verbose=verbose)

        print("Testing utils.system Package...")
        print("-" * 80)

        if "utils" in all_modules:
            utils_system_modules = [
                m for m in all_modules.get("utils", []) if m.startswith("utils.system")
            ]
            for module in utils_system_modules:
                tester.test_module_import(module)

            tester.test_module_attributes(
                "utils.system",
                [
                    "get_device",
                    "get_device_name",
                    "estimate_memory_mb",
                    "get_available_memory_mb",
                    "set_seed",
                    "is_kaggle",
                    "get_environment",
                    "setup_environment",
                    "get_output_path",
                    "get_data_root_path",
                    "get_best_model_path",
                    "run_command",
                    "run_command_with_streaming",
                ],
            )

            tester.test_module_attributes(
                "utils.system.memory",
                [
                    "recover_from_oom",
                    "is_oom_error",
                    "handle_oom_error_with_retry",
                    "cleanup_gpu_memory",
                    "cleanup_dataframe_and_memory",
                    "estimate_memory_mb",
                    "get_available_memory_mb",
                ],
            )

        print()

        print("Testing Contest Package...")
        print("-" * 80)

        if "contest" in all_modules:
            for module in all_modules["contest"]:
                tester.test_module_import(module)

            try:
                registry_module = importlib.import_module("contest.registry")
                tester.test_import(
                    "contest.registry.get_contest_config",
                    lambda: registry_module.get_contest_config(),
                )
                tester.test_import(
                    "contest.registry.get_contest_data_schema",
                    lambda: registry_module.get_contest_data_schema(),
                )
            except (ModuleNotFoundError, ImportError):
                pass

        print()

        print("Testing Config Package...")
        print("-" * 80)

        if "config" in all_modules:
            for module in all_modules["config"]:
                tester.test_module_import(module)

        print()

        for package in [
            "dataset_manipulation",
            "modeling",
            "pipelines",
            "cli",
            "tabular",
            "vision",
        ]:
            if package not in all_modules:
                continue

            print(f"Testing {package.title()} Package...")
            print("-" * 80)

            for module in all_modules[package]:
                tester.test_module_import(module)

            print()

        if "utils" in all_modules:
            print("Testing Utils Package (all modules)...")
            print("-" * 80)

            utils_modules = [
                m for m in all_modules["utils"] if not m.startswith("utils.system")
            ]
            for module in utils_modules:
                tester.test_module_import(module)

            print()

        reporter = TestReporter(tester.results)
        exit_code = reporter.print_summary()
        return ok({"exit_code": int(exit_code)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])