"""Load health JSON report, run threshold checker, derive CLI exit code."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from layers.layer_2_devtools.level_0_infra.level_0.health_thresholds import ThresholdConfig
from layers.layer_2_devtools.level_0_infra.level_1.checker import (
    Severity,
    ThresholdChecker,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.json.report_json import load_json_report


def load_threshold_config(config_path: Optional[Path]) -> ThresholdConfig:
    config = ThresholdConfig()
    if config_path and config_path.is_file():
        import json

        try:
            with open(config_path, encoding="utf-8") as f:
                config = ThresholdConfig.from_dict(json.load(f))
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid threshold config: {e}") from e
    return config


def group_violations_by_severity(
    violations: list,
) -> tuple[list, list, list]:
    fails = [v for v in violations if v.severity == Severity.FAIL]
    warns = [v for v in violations if v.severity == Severity.WARN]
    infos = [v for v in violations if v.severity == Severity.INFO]
    return fails, warns, infos


def print_violations(violations: list, title: str, max_details: int = 5) -> None:
    if not violations:
        return
    print(f"{title} ({len(violations)}):")
    for v in violations:
        print(v)
        for detail in v.details[:max_details]:
            print(detail)
        if len(v.details) > max_details:
            print(f"  ... and {len(v.details) - max_details} more")
        print()


def run_health_threshold_check(
    report_file: Path,
    config_path: Optional[Path],
    strict: bool,
) -> int:
    if not report_file.is_file():
        print(f"Error: Report file not found: {report_file}")
        return 1
    try:
        report = load_json_report(report_file)
    except (OSError, ValueError) as exc:
        print(f"Error: Invalid or unreadable health report: {exc}")
        return 1
    try:
        config = load_threshold_config(config_path)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    print("=" * 80)
    print("PACKAGE HEALTH THRESHOLD CHECK")
    print("=" * 80)
    print(f"Report: {report_file}")
    print(f"Strict mode: {strict}")
    print()

    checker = ThresholdChecker(config)
    _passed, violations = checker.check(report)

    fails, warns, infos = group_violations_by_severity(violations)
    print_violations(fails, "FAILURES", max_details=5)
    print_violations(warns, "WARNINGS", max_details=5)
    print_violations(infos, "INFO", max_details=3)

    print("=" * 80)

    if fails:
        print("HEALTH CHECK FAILED")
        print("Fix critical violations before committing.")
        return 1
    if warns and strict:
        print("HEALTH CHECK FAILED (strict mode)")
        print("Address warnings before committing.")
        return 2
    if warns:
        print("HEALTH CHECK PASSED WITH WARNINGS")
        return 0
    print("HEALTH CHECK PASSED")
    return 0
