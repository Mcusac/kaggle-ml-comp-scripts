"""Auto-generated package exports."""


from .audit_machine_emit_templates import (
    build_audit_markdown,
    build_inventory_markdown,
)

from .base_health_reporter import BaseReporter

from .console_format_helpers import FormattingHelpers

from .health_report_views import (
    DEFAULT_COMPLEXITY_TARGET_NAMES,
    extract_duplicate_blocks,
    lines_complexity_targets,
    lines_duplication_summary,
    lines_health_compare,
    lines_srp_summary,
    remap_duplicate_loc,
)

from .inventory_bootstrap_markdown import bootstrap_markdown

from .move_plan_from_scan import build_move_plan_markdown
from .scan_violation_summary import format_scan_violation_summary_lines

from .import_organizer import (
    ImportOrganizerResult,
    ImportOrganizerSpanResult,
    build_import_organizer_span_edit,
    organize_imports_text,
)

from .promotion_demotion_suggestions_markdown import (
    build_promotion_demotion_suggestions_markdown,
)

from .architecture_score import (
    ScoreComponent,
    ScoreConfig,
    ScoreResult,
    compute_architecture_score,
    load_score_config_optional,
)

from .architecture_scorecard_markdown import (
    ScorecardOptions,
    build_health_markdown_scorecard,
    build_manifest_markdown_scorecard,
    load_health_report,
    load_manifest,
)

__all__ = [
    "BaseReporter",
    "DEFAULT_COMPLEXITY_TARGET_NAMES",
    "FormattingHelpers",
    "bootstrap_markdown",
    "build_audit_markdown",
    "build_inventory_markdown",
    "extract_duplicate_blocks",
    "build_move_plan_markdown",
    "format_scan_violation_summary_lines",
    "ImportOrganizerResult",
    "ImportOrganizerSpanResult",
    "lines_complexity_targets",
    "lines_duplication_summary",
    "lines_health_compare",
    "lines_srp_summary",
    "build_import_organizer_span_edit",
    "organize_imports_text",
    "remap_duplicate_loc",
    "build_promotion_demotion_suggestions_markdown",
    "ScoreComponent",
    "ScoreConfig",
    "ScoreResult",
    "compute_architecture_score",
    "load_score_config_optional",
    "ScorecardOptions",
    "build_health_markdown_scorecard",
    "build_manifest_markdown_scorecard",
    "load_health_report",
    "load_manifest",
]
