"""Unit tests for ImportSurfaceValidator (strict policy).

Note: we use `unittest` instead of pytest because the repo's pytest conftest
imports optional heavy dependencies that may not be installed locally.
"""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

_SCRIPTS = Path(__file__).resolve().parents[5]

if "layers" not in sys.modules:
    pkg = types.ModuleType("layers")
    pkg.__path__ = [str(_SCRIPTS / "layers")]
    sys.modules["layers"] = pkg

# Also bypass auto-generated `__init__.py` side effects in these packages.
if "layers.layer_2_devtools" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools")
    p.__path__ = [str(_SCRIPTS / "layers" / "layer_2_devtools")]
    sys.modules["layers.layer_2_devtools"] = p
if "layers.layer_2_devtools.level_0_infra" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra")
    p.__path__ = [str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra")]
    sys.modules["layers.layer_2_devtools.level_0_infra"] = p
if "layers.layer_2_devtools.level_0_infra.level_0" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra.level_0")
    p.__path__ = [
        str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0")
    ]
    sys.modules["layers.layer_2_devtools.level_0_infra.level_0"] = p


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_SURFACE = _load_module_from_path(
    "_import_surface_validator",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_1"
    / "health_analyzers"
    / "import_surface_validator.py",
)

ImportSurfaceValidator = _SURFACE.ImportSurfaceValidator


def _kinds(report: dict) -> list[str]:
    return [v.get("kind", "") for v in report.get("violations", [])]


class TestImportSurfaceValidator(unittest.TestCase):
    def test_relative_import_forbidden_in_logic(self) -> None:
        with TemporaryDirectory() as td:
            tmp_path = Path(td)
            core = tmp_path / "layer_0_core"
            f = core / "level_1" / "a.py"
            f.parent.mkdir(parents=True)
            f.write_text("from .sibling import x\n", encoding="utf-8")
            (core / "level_1" / "sibling.py").write_text("x = 1\n", encoding="utf-8")

            rep = ImportSurfaceValidator(core).analyze()
            self.assertIn("RELATIVE_IN_LOGIC", _kinds(rep))
            rel = [v for v in rep["violations"] if v["kind"] == "RELATIVE_IN_LOGIC"][0]
            self.assertEqual(rel["line"], 1)

    def test_upward_import_flagged(self) -> None:
        with TemporaryDirectory() as td:
            tmp_path = Path(td)
            core = tmp_path / "layer_0_core"
            f = core / "level_1" / "a.py"
            f.parent.mkdir(parents=True)
            f.write_text("from level_3 import x\n", encoding="utf-8")
            rep = ImportSurfaceValidator(core).analyze()
            self.assertIn("UPWARD", _kinds(rep))

    def test_wrong_level_barrel_flagged(self) -> None:
        with TemporaryDirectory() as td:
            tmp_path = Path(td)
            core = tmp_path / "layer_0_core"
            f = core / "level_2" / "a.py"
            f.parent.mkdir(parents=True)
            f.write_text("from level_2 import x\n", encoding="utf-8")
            rep = ImportSurfaceValidator(core).analyze()
            self.assertIn("WRONG_LEVEL", _kinds(rep))

    def test_deep_level_path_and_missing_module_flagged(self) -> None:
        with TemporaryDirectory() as td:
            tmp_path = Path(td)
            core = tmp_path / "layer_0_core"
            (core / "level_0").mkdir(parents=True)
            (core / "level_0" / "__init__.py").write_text("", encoding="utf-8")
            f = core / "level_1" / "a.py"
            f.parent.mkdir(parents=True)
            f.write_text("from level_0.missing_mod import x\n", encoding="utf-8")
            rep = ImportSurfaceValidator(core).analyze()
            kinds = set(_kinds(rep))
            self.assertIn("DEEP_LEVEL_PATH", kinds)
            self.assertIn("INTERNAL_MODULE_NOT_FOUND", kinds)

    def test_deep_import_suggests_barrel_when_exported(self) -> None:
        with TemporaryDirectory() as td:
            tmp_path = Path(td)
            core = tmp_path / "layer_0_core"
            level0 = core / "level_0"
            level0.mkdir(parents=True)
            (level0 / "__init__.py").write_text(
                "from .submod import exported\n__all__ = ('exported',)\n",
                encoding="utf-8",
            )
            (level0 / "submod.py").write_text("exported = 1\n", encoding="utf-8")

            f = core / "level_1" / "a.py"
            f.parent.mkdir(parents=True)
            f.write_text("from level_0.submod import exported\n", encoding="utf-8")

            rep = ImportSurfaceValidator(core).analyze()
            canon = [
                v
                for v in rep["violations"]
                if v["kind"] == "DEEP_LEVEL_PATH_CANONICAL" and v.get("name") == "exported"
            ]
            self.assertTrue(canon)
            self.assertEqual(canon[0]["suggested"], "from level_0 import exported")


if __name__ == "__main__":
    unittest.main()

