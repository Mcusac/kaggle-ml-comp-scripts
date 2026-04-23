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
if "layers.layer_2_devtools.level_0_infra.level_1" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra.level_1")
    p.__path__ = [
        str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_1")
    ]
    sys.modules["layers.layer_2_devtools.level_0_infra.level_1"] = p
if "layers.layer_2_devtools.level_0_infra.level_1.health_analyzers" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra.level_1.health_analyzers")
    p.__path__ = [
        str(
            _SCRIPTS
            / "layers"
            / "layer_2_devtools"
            / "level_0_infra"
            / "level_1"
            / "health_analyzers"
        )
    ]
    sys.modules["layers.layer_2_devtools.level_0_infra.level_1.health_analyzers"] = p

def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_BASE_ANALYZER = _load_module_from_path(
    "_base_health_analyzer",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "base_health_analyzer.py",
)
_THRESH_CFG = _load_module_from_path(
    "_threshold_config",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "health_thresholds"
    / "config.py",
)

sys.modules["layers.layer_2_devtools.level_0_infra.level_0"].BaseAnalyzer = _BASE_ANALYZER.BaseAnalyzer
sys.modules["layers.layer_2_devtools.level_0_infra.level_0"].ThresholdConfig = _THRESH_CFG.ThresholdConfig

_DEEP_NESTING = _load_module_from_path(
    "_deep_nesting_analyzer",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_1"
    / "health_analyzers"
    / "deep_nesting.py",
)
_CHECKER = _load_module_from_path(
    "_threshold_checker",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_1"
    / "checker.py",
)

DeepNestingAnalyzer = _DEEP_NESTING.DeepNestingAnalyzer
ThresholdChecker = _CHECKER.ThresholdChecker
ThresholdConfig = _THRESH_CFG.ThresholdConfig


class TestDeepNestingAnalyzer(unittest.TestCase):
    def test_counts_code_containing_dirs_and_depth(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            (root / "a" / "b" / "c").mkdir(parents=True)
            (root / "a" / "b" / "c" / "mod.py").write_text("x = 1\n", encoding="utf-8")
            (root / "a" / "b" / "c" / "other.py").write_text("y = 2\n", encoding="utf-8")

            (root / "shallow").mkdir(parents=True)
            (root / "shallow" / "s.py").write_text("z = 3\n", encoding="utf-8")

            rep = DeepNestingAnalyzer(root).analyze()
            self.assertEqual(rep["max_depth"], 3)

            by_dir = {d["dir"]: d for d in rep["deep_dirs"]}
            self.assertEqual(by_dir["a/b/c"]["depth"], 3)
            self.assertEqual(by_dir["a/b/c"]["py_files"], 2)
            self.assertEqual(by_dir["shallow"]["depth"], 1)
            self.assertEqual(by_dir["shallow"]["py_files"], 1)

    def test_threshold_checker_warns_when_too_many_offenders(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            (root / "x" / "y").mkdir(parents=True)
            (root / "x" / "y" / "a.py").write_text("x = 1\n", encoding="utf-8")
            (root / "p" / "q").mkdir(parents=True)
            (root / "p" / "q" / "b.py").write_text("x = 2\n", encoding="utf-8")

            nesting = DeepNestingAnalyzer(root).analyze()
            cfg = ThresholdConfig(max_directory_depth=1, max_deep_directories=0)
            checker = ThresholdChecker(cfg)
            _ok, violations = checker.check({"deep_nesting": nesting})

            cats = [v.category for v in violations]
            self.assertIn("deep_nesting", cats)


if __name__ == "__main__":
    unittest.main()

