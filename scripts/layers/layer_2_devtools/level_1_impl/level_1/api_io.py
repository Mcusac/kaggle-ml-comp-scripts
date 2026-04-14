"""Public API: JSON report loading and AST helpers (delegates to infra only)."""

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    count_class_nodes,
    count_function_nodes,
    count_lines_in_node,
    get_all_classes,
    get_all_functions,
    get_function_complexity,
    get_imports_from_ast,
    get_imports_from_file,
    get_relative_imports_from_ast,
    parse_file,
    resolve_relative_import,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.json.report_json import (
    load_json_report,
)

_resolve_relative_import = resolve_relative_import


def load_json_report_api(config: dict[str, Any]) -> dict[str, Any]:
    """Load a JSON report file with tolerant parsing.

    Args:
        config: ``path`` — file path (str or Path).

    Returns:
        Envelope; on success ``data["report"]`` is the parsed object.
    """
    try:
        p = config.get("path")
        if p is None:
            return {"status": "error", "data": {}, "errors": ["path is required"]}
        report = load_json_report(Path(p))
        return {"status": "ok", "data": {"report": report}, "errors": []}
    except (OSError, TypeError, ValueError) as exc:
        return {"status": "error", "data": {}, "errors": [str(exc)]}