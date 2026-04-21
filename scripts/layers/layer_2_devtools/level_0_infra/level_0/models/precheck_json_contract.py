"""Contract for ``precheck_*.json`` artifacts under ``.cursor/audit-results/.../summaries/``.

CI and strict mode rely on ``precheck_status`` and required keys so machine runs
never masquerade as successful process exits when the scan did not run.
"""

from __future__ import annotations

from typing import Any

# Written when ``audit_precheck`` could not import or run the devtools stack.
PRECHECK_STATUS_SKIPPED_MACHINE = "skipped_machine_script"

# Written when static analysis completed and JSON was persisted.
PRECHECK_STATUS_OK = "ok"

ALLOWED_PRECHECK_STATUSES = frozenset(
    {
        PRECHECK_STATUS_OK,
        PRECHECK_STATUS_SKIPPED_MACHINE,
    }
)


def validate_precheck_json(data: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors; empty if the dict is acceptable.

    Supports:
    - **stub / skip** payloads (missing optional deps): ``precheck_status: skipped_machine_script``
    - **machine** payloads from ``build_precheck_json`` / general stack precheck: scans with
      ``violations`` / ``parse_errors`` lists (and optional ``precheck_status: ok``).
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["payload must be a JSON object"]

    if "generated" not in data:
        errors.append("missing `generated`")

    status = data.get("precheck_status")
    if status is not None and status not in ALLOWED_PRECHECK_STATUSES:
        errors.append(
            f"unknown `precheck_status`: {status!r} (expected one of {sorted(ALLOWED_PRECHECK_STATUSES)})"
        )

    if status == PRECHECK_STATUS_SKIPPED_MACHINE:
        for key in ("audit_scope", "level_name", "artifact_kind", "reason"):
            if key not in data:
                errors.append(f"missing `{key}` (required when precheck_status is skipped)")
        return errors

    # Machine-backed precheck (per-target or general stack): scan results.
    if "violations" in data or "parse_errors" in data:
        for key in ("violations", "parse_errors"):
            if key not in data:
                errors.append(f"missing `{key}`")
            elif not isinstance(data[key], list):
                errors.append(f"`{key}` must be a list")
        if "scope" not in data:
            errors.append("missing `scope`")
        if status is not None and status not in (PRECHECK_STATUS_OK,):
            errors.append("machine payload must use precheck_status ok when set")
        return errors

    errors.append("unrecognized precheck JSON shape (expected skipped_machine_script or scan payload)")
    return errors


def is_machine_precheck_ok(data: dict[str, Any]) -> bool:
    """True when static precheck ran (not a skip stub)."""
    if data.get("precheck_status") == PRECHECK_STATUS_SKIPPED_MACHINE:
        return False
    if data.get("precheck_status") == PRECHECK_STATUS_OK:
        return True
    return "violations" in data or "parse_errors" in data
