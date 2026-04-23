from __future__ import annotations

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
if "layers.layer_2_devtools" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools")
    p.__path__ = [str(_SCRIPTS / "layers" / "layer_2_devtools")]
    sys.modules["layers.layer_2_devtools"] = p
if "layers.layer_2_devtools.level_1_impl" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_1_impl")
    p.__path__ = [str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_1_impl")]
    sys.modules["layers.layer_2_devtools.level_1_impl"] = p
if "layers.layer_2_devtools.level_1_impl.level_2" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_1_impl.level_2")
    p.__path__ = [
        str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_1_impl" / "level_2")
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


_MOD = _load_module_from_path(
    "_dead_symbol_detector",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "dead_symbol_detector.py",
)

_compute = _MOD._compute_run_payload


class TestDeadSymbolDetector(unittest.TestCase):
    def test_combines_unreferenced_and_unreachable(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            pkg = root / "pkg"
            pkg.mkdir(parents=True)

            (pkg / "a.py").write_text(
                "def used():\n"
                "    return 1\n"
                "\n"
                "def dead():\n"
                "    return 2\n",
                encoding="utf-8",
            )
            (pkg / "b.py").write_text(
                "from pkg.a import used\n"
                "x = used()\n",
                encoding="utf-8",
            )

            payload = _compute(
                root=root,
                include_tests=False,
                config=_MOD.DeadSymbolConfig.default(),
                generated=_MOD.date.fromisoformat("2026-04-22"),
                workspace=root,
            )
            self.assertEqual(payload["schema"], "dead_symbol_detector_run.v1")
            self.assertIn("pkg.a:dead", payload["unreferenced_symbol_ids"])
            self.assertIn("pkg.a:dead", payload["unreachable_symbol_ids"])
            self.assertNotIn("pkg.a:used", payload["unreferenced_symbol_ids"])
            self.assertNotIn("pkg.a:used", payload["unreachable_symbol_ids"])


if __name__ == "__main__":
    unittest.main()

