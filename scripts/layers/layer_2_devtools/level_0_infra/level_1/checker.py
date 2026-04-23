"""Compare health analysis dicts against ThresholdConfig."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import ThresholdConfig


class Severity(Enum):
    FAIL = "fail"
    WARN = "warn"
    INFO = "info"


@dataclass
class ThresholdViolation:
    category: str
    severity: Severity
    message: str
    details: list[str]

    def __str__(self) -> str:
        emoji = {"fail": "❌", "warn": "⚠️", "info": "ℹ️"}
        return f"{emoji[self.severity.value]} {self.message}"


class ThresholdChecker:
    def __init__(self, config: ThresholdConfig | None = None):
        self.config = config or ThresholdConfig()
        self.violations: list[ThresholdViolation] = []

    def check(self, results: dict[str, Any]) -> tuple[bool, list[ThresholdViolation]]:
        self.violations = []
        if "file_metrics" in results:
            self._check_file_metrics(results["file_metrics"])
        if "complexity" in results:
            self._check_complexity(results["complexity"])
        if "deep_nesting" in results:
            self._check_deep_nesting(results["deep_nesting"])
        if "cohesion" in results:
            self._check_cohesion(results["cohesion"])
        if "imports" in results:
            self._check_imports(results["imports"])
        if "duplication" in results:
            self._check_duplication(results["duplication"])
        if "dead_code" in results:
            self._check_dead_code(results["dead_code"])
        has_failures = any(v.severity == Severity.FAIL for v in self.violations)
        return not has_failures, self.violations

    def _check_file_metrics(self, metrics: dict[str, Any]) -> None:
        long_files = [
            f for f in metrics.get("long_files", []) if f["lines"] > self.config.max_file_lines
        ]
        if long_files:
            details = [f"  {f['module']}: {f['lines']} lines" for f in long_files[:10]]
            if len(long_files) > 10:
                details.append(f"  ... and {len(long_files) - 10} more")
            self.violations.append(
                ThresholdViolation(
                    category="file_metrics",
                    severity=Severity.FAIL,
                    message=f"{len(long_files)} file(s) exceed {self.config.max_file_lines} lines",
                    details=details,
                )
            )

    def _check_complexity(self, complexity: dict[str, Any]) -> None:
        high_complexity_funcs = [
            f
            for f in complexity.get("functions", [])
            if f["complexity"] > self.config.max_function_complexity
        ]
        if high_complexity_funcs:
            details = [
                f"  {f['module']}.{f['name']}: complexity {f['complexity']}"
                for f in high_complexity_funcs[:10]
            ]
            if len(high_complexity_funcs) > 10:
                details.append(f"  ... and {len(high_complexity_funcs) - 10} more")
            self.violations.append(
                ThresholdViolation(
                    category="complexity",
                    severity=Severity.WARN,
                    message=(
                        f"{len(high_complexity_funcs)} function(s) exceed complexity "
                        f"{self.config.max_function_complexity}"
                    ),
                    details=details,
                )
            )

    def _check_deep_nesting(self, nesting: dict[str, Any]) -> None:
        deep_dirs = nesting.get("deep_dirs", []) or []
        max_depth = int(getattr(self.config, "max_directory_depth", 6))
        max_dirs = int(getattr(self.config, "max_deep_directories", 30))

        offenders = [d for d in deep_dirs if int(d.get("depth", 0)) > max_depth]
        if len(offenders) <= max_dirs:
            return

        details = []
        for row in offenders[:10]:
            d = row.get("dir", "<?>")
            depth = int(row.get("depth", 0))
            py_files = int(row.get("py_files", 0))
            details.append(f"  {d}: depth {depth} ({py_files} .py files)")
        if len(offenders) > 10:
            details.append(f"  ... and {len(offenders) - 10} more")

        self.violations.append(
            ThresholdViolation(
                category="deep_nesting",
                severity=Severity.WARN,
                message=(
                    f"{len(offenders)} directories exceed depth {max_depth} "
                    f"(target ≤{max_dirs})"
                ),
                details=details,
            )
        )

    def _check_cohesion(self, cohesion: dict[str, Any]) -> None:
        low_cohesion = []
        for pkg, stats in cohesion.items():
            if pkg == "__pycache__":
                continue
            pct = stats.get("internal_pct", 0)
            if pct < self.config.min_package_cohesion_pct:
                low_cohesion.append((pkg, pct))
        if low_cohesion:
            details = [
                f"  {pkg}: {pct}% cohesion (target {self.config.min_package_cohesion_pct}%)"
                for pkg, pct in low_cohesion
            ]
            self.violations.append(
                ThresholdViolation(
                    category="cohesion",
                    severity=Severity.WARN,
                    message=(
                        f"{len(low_cohesion)} package(s) below "
                        f"{self.config.min_package_cohesion_pct}% cohesion"
                    ),
                    details=details,
                )
            )

    def _check_imports(self, imports: dict[str, Any]) -> None:
        deep = imports.get("deep_cross_package", [])
        if len(deep) > self.config.max_deep_imports:
            details = [f"  {imp['importer']} → {imp['imported']}" for imp in deep[:5]]
            self.violations.append(
                ThresholdViolation(
                    category="imports",
                    severity=Severity.WARN,
                    message=(
                        f"{len(deep)} depth-{self.config.max_import_depth}+ cross-package imports "
                        f"(target <{self.config.max_deep_imports})"
                    ),
                    details=details,
                )
            )

    def _check_duplication(self, duplication: dict[str, Any]) -> None:
        blocks = duplication.get("duplicate_blocks", [])
        if len(blocks) > self.config.max_duplicate_blocks:
            details = [
                f"  {block['file1']} ≈ {block['file2']}: {block['lines']} lines"
                for block in blocks[:5]
            ]
            self.violations.append(
                ThresholdViolation(
                    category="duplication",
                    severity=Severity.WARN,
                    message=(
                        f"{len(blocks)} duplicate code blocks found "
                        f"(target ≤{self.config.max_duplicate_blocks})"
                    ),
                    details=details,
                )
            )
        high_frequency = [
            block
            for block in blocks
            if block.get("frequency", 2) >= self.config.min_duplicate_frequency_for_warning
            and block.get("lines", 0) > 10
        ]
        if len(high_frequency) > self.config.max_actionable_duplicate_blocks:
            details = [
                f"  {block['file1']}:{block['line1']} ≈ {block['file2']}:{block['line2']} "
                f"({block['lines']} lines, frequency: {block.get('frequency', 2)})"
                for block in high_frequency[:5]
            ]
            self.violations.append(
                ThresholdViolation(
                    category="duplication",
                    severity=Severity.WARN,
                    message=(
                        f"{len(high_frequency)} actionable duplicate blocks found "
                        f"(appear in {self.config.min_duplicate_frequency_for_warning}+ files, >10 lines). "
                        f"Target ≤{self.config.max_actionable_duplicate_blocks}"
                    ),
                    details=details,
                )
            )

    def _check_dead_code(self, dead_code: dict[str, Any]) -> None:
        unused = dead_code.get("unused_imports", [])
        if len(unused) > self.config.max_unused_imports:
            details = [
                f"  {imp['module']}: {', '.join(imp['names'][:3])}" for imp in unused[:5]
            ]
            self.violations.append(
                ThresholdViolation(
                    category="dead_code",
                    severity=Severity.INFO,
                    message=f"{len(unused)} module(s) with unused imports",
                    details=details,
                )
            )