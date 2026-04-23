"""Unit tests for ``run_code_audit_pipeline`` (manifest + discovery only; fast)."""

import json
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[5]


def test_code_audit_pipeline_manifest_schema(tmp_path: Path) -> None:
    from layers.layer_2_devtools.level_1_impl.level_2.pipeline_ops import run_code_audit_pipeline

    out = run_code_audit_pipeline(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "output_dir": tmp_path,
            "run_id": "pytest-pipeline-000",
            "max_targets": 1,
            "run_precheck": False,
            "run_general_stack_scan": False,
            "run_oversized_module_scan": False,
            "run_csiro_scan": False,
        }
    )
    assert out["status"] == "ok"
    mpath = Path(out["data"]["manifest_path"])
    assert mpath == tmp_path / "manifest.json"
    assert mpath.is_file()
    man = json.loads(mpath.read_text(encoding="utf-8"))
    assert man["schema_version"] == "1"
    assert man["run_id"] == "pytest-pipeline-000"
    assert man["aggregate"]["overall_exit_code"] == 0
    assert man["steps"]["precheck"]["status"] == "skipped"
    assert man["steps"]["general_stack_scan"]["status"] == "skipped"
    assert man["steps"]["oversized_module_scan"]["status"] == "skipped"
    assert man["steps"]["csiro_scan"]["status"] == "skipped"
    qfile = tmp_path / "audit_queue.json"
    assert qfile.is_file()


def test_code_audit_pipeline_fail_on_skipped(tmp_path: Path) -> None:
    from layers.layer_2_devtools.level_1_impl.level_2.pipeline_ops import run_code_audit_pipeline

    out = run_code_audit_pipeline(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "output_dir": tmp_path,
            "run_id": "pytest-pipeline-fail-skip",
            "max_targets": 1,
            "run_precheck": False,
            "run_general_stack_scan": False,
            "run_oversized_module_scan": False,
            "run_csiro_scan": False,
            "fail_on_skipped": True,
        }
    )
    assert out["status"] == "ok"
    man = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert man["aggregate"]["overall_exit_code"] == 1
    fs = man["aggregate"]["failed_steps"]
    assert any(s.startswith("skipped:precheck") for s in fs)
    assert any(s.startswith("skipped:general_stack_scan") for s in fs)
    assert any(s.startswith("skipped:oversized_module_scan") for s in fs)
    assert any(s.startswith("skipped:csiro_scan") for s in fs)
