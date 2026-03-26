"""Run full package health analysis (analyzer fan-in + reporter)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.format.health_reporters import JSONReporter
from layers.layer_2_devtools.level_0_infra.level_2 import (
    ConsoleReporter,
)
from layers.layer_2_devtools.level_0_infra.level_0.format.health_report_views import (
    DEFAULT_COMPLEXITY_TARGET_NAMES,
    lines_complexity_targets,
    lines_duplication_summary,
    lines_health_compare,
    lines_srp_summary,
)
from layers.layer_2_devtools.level_0_infra.level_0.health_thresholds import ThresholdConfig
from layers.layer_2_devtools.level_0_infra.level_0.parse.json.report_json import load_json_report
from layers.layer_2_devtools.level_0_infra.level_0.scan.health_analyzers import (
    CohesionAnalyzer,
    ComplexityAnalyzer,
    DeadCodeFinder,
    DependencyRuleAnalyzer,
    DuplicationDetector,
    FileMetricsAnalyzer,
    ImportAnalyzer,
    ImportPathValidator,
    SOLIDChecker,
    TypeAnnotationChecker,
)


@dataclass
class PackageHealthRunOptions:
    root: Path
    config: ThresholdConfig
    no_complexity: bool = False
    no_duplication: bool = False
    no_solid: bool = False
    no_dead_code: bool = False
    as_json: bool = False


def collect_health_results(opts: PackageHealthRunOptions) -> dict[str, Any]:
    """Execute analyzers and return the raw results dict (before reporter formatting)."""
    root = opts.root
    config = opts.config
    results: dict[str, Any] = {"root": str(root)}

    print("📄 Analyzing file metrics...")
    results["file_metrics"] = FileMetricsAnalyzer(root).analyze()

    if not opts.no_complexity:
        print("🔢 Analyzing complexity...")
        results["complexity"] = ComplexityAnalyzer(root).analyze()

    print("📦 Analyzing imports...")
    results["imports"] = ImportAnalyzer(root).analyze()

    print("🔍 Validating import paths...")
    results["import_paths"] = ImportPathValidator(root).analyze()

    print("📝 Checking type annotations...")
    results["type_annotations"] = TypeAnnotationChecker(root).analyze()

    print("🎯 Analyzing package cohesion...")
    results["cohesion"] = CohesionAnalyzer(root).analyze()

    print("📐 Checking dependency rules...")
    results["dependency_rule"] = DependencyRuleAnalyzer(root).analyze()

    if not opts.no_duplication:
        print("🔄 Detecting code duplication...")
        results["duplication"] = DuplicationDetector(
            root, min_lines=config.min_duplicate_lines
        ).analyze()

    if not opts.no_solid:
        print("🏛️ Checking SOLID principles...")
        results["solid"] = SOLIDChecker(root).analyze()

    if not opts.no_dead_code:
        print("💀 Finding dead code...")
        results["dead_code"] = DeadCodeFinder(root).analyze()

    return results


def run_package_health_cli(opts: PackageHealthRunOptions) -> str:
    """Run analysis and return the final report string (console or JSON)."""
    results = collect_health_results(opts)
    reporter: ConsoleReporter | JSONReporter
    if opts.as_json:
        reporter = JSONReporter()
    else:
        reporter = ConsoleReporter()
    return reporter.report(results)


@dataclass
class HealthSummaryOptions:
    root: Path
    output_json: Path
    previous: Path | None
    config: ThresholdConfig
    skip_duplication: bool
    skip_solid: bool
    skip_dead_code: bool


def run_health_summary(opts: HealthSummaryOptions) -> int:
    """Run package health, write JSON report, print summary blocks. Returns aggregate exit code."""
    ro = PackageHealthRunOptions(
        root=opts.root,
        config=opts.config,
        no_complexity=False,
        no_duplication=opts.skip_duplication,
        no_solid=opts.skip_solid,
        no_dead_code=opts.skip_dead_code,
        as_json=True,
    )
    results = collect_health_results(ro)
    opts.output_json.parent.mkdir(parents=True, exist_ok=True)
    opts.output_json.write_text(JSONReporter().report(results), encoding="utf-8")
    print("\n✅ Wrote JSON report.")

    rc = 0
    data = load_json_report(opts.output_json)

    print("\n=== RUNNING SUMMARIES (in-process) ===")
    for line in lines_complexity_targets(
        data, report_path=opts.output_json, targets=list(DEFAULT_COMPLEXITY_TARGET_NAMES)
    ):
        print(line)
    for line in lines_srp_summary(data, report_path=opts.output_json, top_modules=20):
        print(line)
    for line in lines_duplication_summary(
        data, report_path=opts.output_json, top=20
    ):
        print(line)

    if opts.previous is not None and opts.previous.is_file():
        prev = load_json_report(opts.previous)
        for line in lines_health_compare(
            prev, data, pre_path=opts.previous, post_path=opts.output_json
        ):
            print(line)
    elif opts.previous is not None:
        print(f"⚠️ Previous report not found at {opts.previous}, skipping comparison.")

    return rc
