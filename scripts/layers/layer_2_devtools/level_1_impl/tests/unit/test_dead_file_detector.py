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
    "_dead_file_detector",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "dead_file_detector.py",
)

_compute = _MOD._compute_candidates


class TestDeadFileDetector(unittest.TestCase):
    def test_orphans_and_unreachable(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            pkg = root / "pkg"
            pkg.mkdir(parents=True)

            (pkg / "__init__.py").write_text("", encoding="utf-8")

            (pkg / "entry.py").write_text(
                "from pkg.reachable import f\n"
                "x = f()\n",
                encoding="utf-8",
            )
            (pkg / "reachable.py").write_text(
                "def f():\n"
                "    return 1\n",
                encoding="utf-8",
            )

            (pkg / "orphan.py").write_text("x = 1\n", encoding="utf-8")

            (pkg / "cluster_a.py").write_text(
                "from pkg.cluster_b import b\n"
                "def a():\n"
                "    return b()\n",
                encoding="utf-8",
            )
            (pkg / "cluster_b.py").write_text(
                "from pkg.cluster_a import a\n"
                "def b():\n"
                "    return 2\n",
                encoding="utf-8",
            )

            cfg = _MOD.DeadFileConfig(
                entrypoint_modules=frozenset({"pkg.entry"}),
                allow_modules=frozenset(),
                allow_module_prefixes=(),
            )
            payload = _compute(root=root, config=cfg, include_tests=False)

            self.assertEqual(payload["schema"], "dead_file_detector_run.v1")

            self.assertIn("pkg.orphan", payload["orphan_modules"])
            self.assertNotIn("pkg.entry", payload["orphan_modules"])
            self.assertNotIn("pkg.reachable", payload["orphan_modules"])

            self.assertIn("pkg.orphan", payload["unreachable_modules"])
            self.assertIn("pkg.cluster_a", payload["unreachable_modules"])
            self.assertIn("pkg.cluster_b", payload["unreachable_modules"])
            self.assertNotIn("pkg.entry", payload["unreachable_modules"])
            self.assertNotIn("pkg.reachable", payload["unreachable_modules"])


if __name__ == "__main__":
    unittest.main()

