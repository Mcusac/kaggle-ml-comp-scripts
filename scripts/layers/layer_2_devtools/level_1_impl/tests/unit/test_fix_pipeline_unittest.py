"""Unit tests for the code-fix machine pipeline.

Note: use `unittest` to avoid importing repo-level pytest conftest (may pull heavy deps).
"""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

_SCRIPTS = Path(__file__).resolve().parents[5]


def _ensure_pkg(name: str, path: Path) -> None:
    if name in sys.modules:
        return
    pkg = types.ModuleType(name)
    pkg.__path__ = [str(path)]
    sys.modules[name] = pkg


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Keep imports lightweight and avoid executing unrelated package __init__.py.
_ensure_pkg("layers", _SCRIPTS / "layers")
_ensure_pkg("layers.layer_2_devtools", _SCRIPTS / "layers" / "layer_2_devtools")
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_1_impl",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl.level_2",
    _SCRIPTS / "layers" / "layer_2_devtools" / "level_1_impl" / "level_2",
)

_PIPE = _load_module_from_path(
    "_fix_pipeline_ops",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "fix_pipeline_ops.py",
)

run_code_fix_pipeline = _PIPE.run_code_fix_pipeline


class TestFixPipeline(unittest.TestCase):
    def test_writes_fix_run_artifact_even_when_all_steps_skipped(self) -> None:
        with TemporaryDirectory() as td:
            artifact_base = Path(td) / "input" / "kaggle-ml-comp-scripts"
            scripts_root = artifact_base / "scripts"
            layers = scripts_root / "layers"
            target_root = layers / "layer_0_core" / "level_0"

            # Minimal package-like structure so artifact root resolution can anchor.
            (artifact_base / ".cursor" / "audit-results").mkdir(parents=True)
            (layers / "__init__.py").parent.mkdir(parents=True, exist_ok=True)
            layers.mkdir(parents=True, exist_ok=True)
            (layers / "__init__.py").write_text("", encoding="utf-8")
            target_root.mkdir(parents=True)
            (target_root / "__init__.py").write_text("", encoding="utf-8")

            gen = date(2026, 1, 2)
            env = run_code_fix_pipeline(
                {
                    "scripts_root": scripts_root,
                    "target_root": target_root,
                    "generated": gen,
                    "apply": False,
                    "tools": ["apply_violation_fixes"],
                }
            )
            self.assertEqual(env["status"], "ok")
            data = env["data"]
            out_path = Path(data["fix_run_path"])
            self.assertTrue(out_path.exists())
            body = out_path.read_text(encoding="utf-8")
            self.assertIn("FIX_RUN_", out_path.name)
            self.assertIn("apply_violation_fixes", body)
            self.assertIn("skipped", body)


if __name__ == "__main__":
    unittest.main()

