"""Unit tests for audit orchestrator (manifest v2; discovery-only fast path)."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

_SCRIPTS_ROOT = Path(__file__).resolve().parents[5]

if "layers" not in sys.modules:
    pkg = types.ModuleType("layers")
    pkg.__path__ = [str(_SCRIPTS_ROOT / "layers")]
    sys.modules["layers"] = pkg
if "layers.layer_2_devtools" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools")
    p.__path__ = [str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools")]
    sys.modules["layers.layer_2_devtools"] = p
if "layers.layer_2_devtools.level_1_impl" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_1_impl")
    p.__path__ = [str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl")]
    sys.modules["layers.layer_2_devtools.level_1_impl"] = p
if "layers.layer_2_devtools.level_1_impl.level_2" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_1_impl.level_2")
    p.__path__ = [
        str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl" / "level_2")
    ]
    sys.modules["layers.layer_2_devtools.level_1_impl.level_2"] = p


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_OPS = _load_module_from_path(
    "_audit_orchestrator_ops",
    _SCRIPTS_ROOT
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "audit_orchestrator_ops.py",
)


class TestAuditOrchestratorManifestV2(unittest.TestCase):
    def test_manifest_v2_schema(self) -> None:
        with TemporaryDirectory() as td:
            out_dir = Path(td)
            out = _OPS.run_audit_orchestrator(
                {
                    "scripts_root": _SCRIPTS_ROOT,
                    "output_dir": out_dir,
                    "run_id": "unittest-audit-orchestrator-000",
                    "write_queue_json": True,
                    "run_precheck": False,
                    "run_dependency_validation": False,
                    "run_import_validation": False,
                    "run_circular_deps": False,
                    "run_barrel_enforcement": False,
                    "run_dead_symbols": False,
                }
            )
            assert out["status"] == "ok"
            mpath = Path(out["data"]["manifest_path"])
            assert mpath == out_dir / "manifest.json"
            man = json.loads(mpath.read_text(encoding="utf-8"))
            assert man["schema_version"] == "2"
            assert man["run_id"] == "unittest-audit-orchestrator-000"
            assert man["aggregate"]["overall_exit_code"] == 0
            assert man["steps"]["precheck"]["status"] == "skipped"
            assert man["steps"]["dependency_validation"]["status"] == "skipped"
            assert man["steps"]["import_validation"]["status"] == "skipped"
            assert man["steps"]["circular_deps"]["status"] == "skipped"
            assert man["steps"]["barrel_enforcement"]["status"] == "skipped"
            assert man["steps"]["dead_symbols"]["status"] == "skipped"
            assert (out_dir / "audit_queue.json").is_file()

    def test_fail_on_skipped(self) -> None:
        with TemporaryDirectory() as td:
            out_dir = Path(td)
            out = _OPS.run_audit_orchestrator(
                {
                    "scripts_root": _SCRIPTS_ROOT,
                    "output_dir": out_dir,
                    "run_id": "unittest-audit-orchestrator-fail-skip",
                    "write_queue_json": True,
                    "fail_on_skipped": True,
                    "run_precheck": False,
                    "run_dependency_validation": False,
                    "run_import_validation": False,
                    "run_circular_deps": False,
                    "run_barrel_enforcement": False,
                    "run_dead_symbols": False,
                }
            )
            assert out["status"] == "ok"
            man = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
            assert man["aggregate"]["overall_exit_code"] == 1
            fs = man["aggregate"]["failed_steps"]
            assert any(s.startswith("skipped:precheck") for s in fs)
            assert any(s.startswith("skipped:dependency_validation") for s in fs)
            assert any(s.startswith("skipped:import_validation") for s in fs)
            assert any(s.startswith("skipped:circular_deps") for s in fs)
            assert any(s.startswith("skipped:barrel_enforcement") for s in fs)
            assert any(s.startswith("skipped:dead_symbols") for s in fs)


