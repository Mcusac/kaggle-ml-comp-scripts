"""Console reporter for human-readable output."""

from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import (
    BaseReporter,
)
from layers.layer_2_devtools.level_0_infra.level_1 import (
    SectionFormatters,
)


class ConsoleReporter(BaseReporter):
    """
    Generate human-readable console reports.

    Uses emojis and formatting for readability.
    """

    @property
    def format_name(self) -> str:
        return "console"

    def report(self, results: dict[str, Any]) -> str:
        """Generate console report."""
        lines = []

        lines.append("=" * 80)
        lines.append("📊 PACKAGE HEALTH REPORT")
        lines.append("=" * 80)
        lines.append(f"Root: {results.get('root', 'N/A')}")
        lines.append("")

        if "file_metrics" in results:
            lines.extend(SectionFormatters.format_file_metrics(results["file_metrics"]))

        if "complexity" in results:
            lines.extend(SectionFormatters.format_complexity(results["complexity"]))

        if "imports" in results:
            lines.extend(SectionFormatters.format_imports(results["imports"]))

        if "import_paths" in results:
            lines.extend(SectionFormatters.format_import_paths(results["import_paths"]))

        if "type_annotations" in results:
            lines.extend(
                SectionFormatters.format_type_annotations(results["type_annotations"])
            )

        if "cohesion" in results:
            lines.extend(SectionFormatters.format_cohesion(results["cohesion"]))

        if "duplication" in results:
            lines.extend(SectionFormatters.format_duplication(results["duplication"]))

        if "solid" in results:
            lines.extend(SectionFormatters.format_solid(results["solid"]))

        if "dead_code" in results:
            lines.extend(SectionFormatters.format_dead_code(results["dead_code"]))

        if "dependency_rule" in results:
            lines.extend(
                SectionFormatters.format_dependency_rule(results["dependency_rule"])
            )

        lines.append("")
        lines.append("✅ Report complete")

        return "\n".join(lines)
