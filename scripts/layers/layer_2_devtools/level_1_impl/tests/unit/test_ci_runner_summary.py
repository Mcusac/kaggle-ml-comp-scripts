"""Unit tests for `ci_runner` summary helpers (no scans executed)."""

from pathlib import Path


def test_summary_lines_formats_pass_and_steps() -> None:
    from layers.layer_2_devtools.level_1_impl.level_2 import ci_runner

    data = {
        "run_id": "pytest-ci-000",
        "manifest_path": "/tmp/manifest.json",
        "health_report_path": "/tmp/health_report.json",
        "steps": [
            {"name": "code_audit_pipeline", "exit_code": 0, "manifest_path": "/tmp/manifest.json"},
            {"name": "scan_level_violations", "exit_code": 1, "summary_line": "[SUMMARY] Violations: 1"},
        ],
        "overall_exit_code": 1,
    }
    lines = ci_runner._summary_lines(data)
    assert any("CI Runner: FAIL" in ln for ln in lines)
    assert any("code_audit_pipeline" in ln for ln in lines)
    assert any("scan_level_violations" in ln for ln in lines)


def test_write_step_summary_no_env_does_not_crash(monkeypatch) -> None:
    from layers.layer_2_devtools.level_1_impl.level_2 import ci_runner

    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    ci_runner._write_step_summary(lines=["hello"], enabled=True)


def test_write_runner_summary_file(tmp_path: Path) -> None:
    from layers.layer_2_devtools.level_1_impl.level_2 import ci_runner

    out = ci_runner._write_runner_summary_file(
        workspace_root=tmp_path,
        run_id="pytest-ci-run",
        lines=["# hi", "ok"],
    )
    assert out.is_file()
    assert "ci_runs" in str(out)

