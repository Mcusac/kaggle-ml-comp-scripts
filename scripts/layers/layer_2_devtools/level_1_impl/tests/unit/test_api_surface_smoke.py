"""Smoke tests: public devtools API envelope and imports (no impl/level_0 in callers)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[5]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import resolve_workspace
from layers.layer_2_devtools.level_1_impl.level_1.api_discovery import run_audit_target_discovery


def test_resolve_workspace_envelope() -> None:
    env = resolve_workspace({"start": _SCRIPTS})
    assert env["status"] == "ok"
    assert env["errors"] == []
    assert "workspace" in env["data"]


def test_run_audit_target_discovery_envelope() -> None:
    env = run_audit_target_discovery(
        {"scripts_root": _SCRIPTS, "include_markdown": False}
    )
    assert env["status"] == "ok"
    assert "payload" in env["data"]
    assert "json_text" in env["data"]


def test_run_audit_target_discovery_error_on_bad_preset() -> None:
    env = run_audit_target_discovery(
        {"scripts_root": _SCRIPTS, "preset": "nope", "include_markdown": False}
    )
    assert env["status"] == "error"
    assert env["errors"]
