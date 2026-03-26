"""Section formatters for console reporter."""

from typing import Any, List

from layers.layer_2_devtools.level_0_infra.level_0 import FormattingHelpers


class SectionFormatters:
    """Helper class for formatting different report sections."""

    @staticmethod
    def format_file_metrics(metrics: dict[str, Any]) -> List[str]:
        """Format file metrics section."""
        lines = FormattingHelpers.format_section_header("FILE METRICS", "📄")

        long_files = metrics.get("long_files", [])
        if long_files:
            formatter = lambda f: f"{f['lines']:5} lines  {f['module']}"
            lines.extend(
                FormattingHelpers.format_list_with_truncation(
                    long_files, formatter, max_items=20, item_name="Long files"
                )
            )
        else:
            lines.append(FormattingHelpers.format_success_message("No excessively long files"))

        lines.append("")
        return lines

    @staticmethod
    def format_complexity(complexity: dict[str, Any]) -> List[str]:
        """Format complexity section."""
        lines = FormattingHelpers.format_section_header("COMPLEXITY", "🔢")

        high_funcs = [f for f in complexity.get("functions", []) if f["complexity"] > 10]
        if high_funcs:
            formatter = lambda f: (
                f"{f['complexity']:3}  {f['module']}.{f['name']} (line {f['line']})"
            )
            lines.extend(
                FormattingHelpers.format_list_with_truncation(
                    high_funcs,
                    formatter,
                    max_items=15,
                    item_name="High complexity functions",
                )
            )
        else:
            lines.append(
                FormattingHelpers.format_success_message(
                    "All functions have reasonable complexity"
                )
            )

        lines.append("")
        return lines

    @staticmethod
    def format_imports(imports: dict[str, Any]) -> List[str]:
        """Format imports section."""
        lines = list(FormattingHelpers.format_section_header("IMPORTS", "📦"))

        deep = imports.get("deep_cross_package", [])
        if deep:
            lines.append(f"Deep cross-package imports ({len(deep)} total):")
            for imp in deep[:15]:
                lines.append(
                    f"  {imp['importer']} → {imp['imported']} (depth {imp['depth']})"
                )
            if len(deep) > 15:
                lines.append(f"  ... and {len(deep) - 15} more")
        else:
            lines.append("✓ No deep cross-package imports")

        orphans = imports.get("orphans", [])
        if orphans:
            lines.append(f"\nOrphaned modules ({len(orphans)} total):")
            for o in orphans[:15]:
                lines.append(f"  {o}")
            if len(orphans) > 15:
                lines.append(f"  ... and {len(orphans) - 15} more")

        lines.append("")
        return lines

    @staticmethod
    def format_import_paths(paths: dict[str, Any]) -> List[str]:
        """Format import path validation section."""
        lines = list(
            FormattingHelpers.format_section_header("IMPORT PATH VALIDATION", "🔍")
        )

        invalid = paths.get("invalid_imports", [])
        if invalid:
            lines.append(f"Invalid import paths ({len(invalid)} total):")
            for imp in invalid[:20]:
                lines.append(f"  {imp['file']}:{imp['line']} - {imp['original']}")
                lines.append(f"    Resolves to: {imp['resolved']} (does not exist)")
                if imp.get("suggested"):
                    lines.append(f"    Suggested: {imp['suggested']}")
            if len(invalid) > 20:
                lines.append(f"  ... and {len(invalid) - 20} more")
        else:
            lines.append("✓ All import paths are valid")

        lines.append("")
        return lines

    @staticmethod
    def format_type_annotations(annotations: dict[str, Any]) -> List[str]:
        """Format type annotation checker section."""
        lines = list(
            FormattingHelpers.format_section_header("TYPE ANNOTATIONS", "📝")
        )

        missing = annotations.get("missing_imports", [])
        if missing:
            lines.append(f"Missing type annotation imports ({len(missing)} total):")
            for imp in missing[:20]:
                lines.append(f"  {imp['file']}:{imp['line']} - {imp['type']} not imported")
                lines.append(f"    Suggested: {imp['suggested_import']}")
            if len(missing) > 20:
                lines.append(f"  ... and {len(missing) - 20} more")
        else:
            lines.append("✓ All type annotations are properly imported")

        lines.append("")
        return lines

    @staticmethod
    def format_cohesion(cohesion: dict[str, Any]) -> List[str]:
        """Format cohesion section."""
        lines = list(
            FormattingHelpers.format_section_header("PACKAGE COHESION", "🎯")
        )

        for pkg in sorted(cohesion.keys()):
            if pkg == "__pycache__":
                continue
            stats = cohesion[pkg]
            pct = stats.get("internal_pct", 0)
            emoji = "✓" if pct >= 25 else "⚠️"
            lines.append(
                f"  {emoji} {pkg}: {pct}% internal "
                f"(int:{stats['internal']}, ext:{stats['external']}, "
                f"3rd:{stats['third_party']}, files:{stats['files']})"
            )

        lines.append("")
        return lines

    @staticmethod
    def format_duplication(duplication: dict[str, Any]) -> List[str]:
        """Format duplication section."""
        lines = list(
            FormattingHelpers.format_section_header("CODE DUPLICATION", "🔄")
        )

        blocks = duplication.get("duplicate_blocks", [])
        if blocks:
            lines.append(f"Duplicate blocks ({len(blocks)} total):")
            for b in blocks[:10]:
                lines.append(f"  {b['file1']} ≈ {b['file2']} ({b['lines']} lines)")
            if len(blocks) > 10:
                lines.append(f"  ... and {len(blocks) - 10} more")
        else:
            lines.append("✓ No significant code duplication detected")

        lines.append("")
        return lines

    @staticmethod
    def format_solid(solid: dict[str, Any]) -> List[str]:
        """Format SOLID violations section."""
        lines = list(
            FormattingHelpers.format_section_header("SOLID PRINCIPLES", "🏛️")
        )

        srp = solid.get("srp_violations", [])
        if srp:
            lines.append(f"SRP violations ({len(srp)} total):")
            for v in srp[:10]:
                lines.append(f"  {v['module']}.{v['name']}: {v['reason']}")
            if len(srp) > 10:
                lines.append(f"  ... and {len(srp) - 10} more")

        dip = solid.get("dip_violations", [])
        if dip:
            lines.append(f"\nDIP violations ({len(dip)} total):")
            for v in dip[:10]:
                lines.append(f"  {v['module']} → {v['imported']}: {v['reason']}")
            if len(dip) > 10:
                lines.append(f"  ... and {len(dip) - 10} more")

        if not srp and not dip:
            lines.append("✓ No SOLID violations detected")

        lines.append("")
        return lines

    @staticmethod
    def format_dead_code(dead_code: dict[str, Any]) -> List[str]:
        """Format dead code section."""
        lines = list(FormattingHelpers.format_section_header("DEAD CODE", "💀"))

        unused = dead_code.get("unused_imports", [])
        if unused:
            lines.append(f"Modules with unused imports ({len(unused)} total):")
            for u in unused[:10]:
                names = ", ".join(u["names"][:5])
                if len(u["names"]) > 5:
                    names += f" +{len(u['names']) - 5} more"
                lines.append(f"  {u['module']}: {names}")
            if len(unused) > 10:
                lines.append(f"  ... and {len(unused) - 10} more")

        unreachable = dead_code.get("unreachable_code", [])
        if unreachable:
            lines.append(f"\nUnreachable code blocks ({len(unreachable)} total):")
            for u in unreachable[:10]:
                lines.append(
                    f"  {u['module']}.{u['function']}: {u['reason']} (line {u['line']})"
                )
            if len(unreachable) > 10:
                lines.append(f"  ... and {len(unreachable) - 10} more")

        if not unused and not unreachable:
            lines.append("✓ No obvious dead code detected")

        lines.append("")
        return lines

    @staticmethod
    def format_dependency_rule(dependency_rule: dict[str, Any]) -> List[str]:
        """Format dependency rule section (components/core import boundaries)."""
        lines = list(
            FormattingHelpers.format_section_header("DEPENDENCY RULE", "📐")
        )

        violations = dependency_rule.get("violations", [])
        if violations:
            lines.append(f"Dependency rule violations ({len(violations)} total):")
            for v in violations[:20]:
                lines.append(f"  {v['file']}:{v['line']} - imports {v['module']}")
                lines.append(f"    Rule: {v['rule']}")
            if len(violations) > 20:
                lines.append(f"  ... and {len(violations) - 20} more")
        else:
            lines.append("✓ No dependency rule violations (components/core boundaries respected)")

        lines.append("")
        return lines
