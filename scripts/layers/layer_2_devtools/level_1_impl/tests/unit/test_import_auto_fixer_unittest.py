"""Unit tests for the import auto-fixer rewrite engine and strategies.

Note: we use `unittest` here to avoid importing repo-level pytest conftest (may pull heavy deps).
"""

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


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_STRAT = _load_module_from_path(
    "_import_fix_strategies",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "fix"
    / "import_fix_strategies.py",
)
_ENGINE = _load_module_from_path(
    "_import_rewrite_engine",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "fix"
    / "import_rewrite_engine.py",
)

FixOptions = _STRAT.FixOptions
build_edit_operations_for_tree = _STRAT.build_edit_operations_for_tree
apply_edit_operations = _ENGINE.apply_edit_operations


class TestImportAutoFixer(unittest.TestCase):
    def test_deep_level_path_rewrites_when_exported(self) -> None:
        with TemporaryDirectory() as td:
            scripts_root = Path(td) / "scripts"
            layers = scripts_root / "layers"
            core = layers / "layer_0_core"
            layers.mkdir(parents=True)
            (layers / "__init__.py").write_text("", encoding="utf-8")
            core.mkdir(parents=True)
            (core / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_0").mkdir(parents=True)
            (core / "level_1").mkdir(parents=True)
            (core / "level_0" / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_1" / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_0" / "__init__.py").write_text(
                "from .submod import exported\n__all__ = ('exported',)\n",
                encoding="utf-8",
            )
            (core / "level_0" / "submod.py").write_text("exported = 1\n", encoding="utf-8")
            target = core / "level_1" / "a.py"
            target.write_text("from level_0.submod import exported\n", encoding="utf-8")

            ops, errs = build_edit_operations_for_tree(
                root=layers,
                scripts_root=scripts_root,
                opts=FixOptions(include_tests=False, rewrite_relative_in_logic="off"),
            )
            self.assertFalse(errs)
            self.assertEqual(len(ops), 1)
            self.assertTrue(
                ops[0].new_line in ("from level_0 import exported\n", "from level_0 import exported\r\n")
            )

            results, summary, apply_errs = apply_edit_operations(
                ops, apply=True, max_changes_per_file=25
            )
            self.assertFalse(apply_errs)
            self.assertEqual(summary.files_changed, 1)
            self.assertIn("from level_0 import exported", target.read_text(encoding="utf-8"))

    def test_preserves_crlf_newlines(self) -> None:
        with TemporaryDirectory() as td:
            scripts_root = Path(td) / "scripts"
            layers = scripts_root / "layers"
            core = layers / "layer_0_core"
            layers.mkdir(parents=True)
            (layers / "__init__.py").write_text("", encoding="utf-8")
            core.mkdir(parents=True)
            (core / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_0").mkdir(parents=True)
            (core / "level_1").mkdir(parents=True)
            (core / "level_0" / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_1" / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_0" / "__init__.py").write_text(
                "from .submod import exported\r\n__all__ = ('exported',)\r\n",
                encoding="utf-8",
            )
            (core / "level_0" / "submod.py").write_text("exported = 1\r\n", encoding="utf-8")
            target = core / "level_1" / "a.py"
            target.write_bytes(b"from level_0.submod import exported\r\nx = 1\r\n")

            ops, _ = build_edit_operations_for_tree(
                root=layers,
                scripts_root=scripts_root,
                opts=FixOptions(include_tests=False, rewrite_relative_in_logic="off"),
            )
            results, summary, apply_errs = apply_edit_operations(
                ops, apply=True, max_changes_per_file=25
            )
            self.assertFalse(apply_errs)
            self.assertEqual(summary.files_changed, 1)
            self.assertIn(b"\r\n", target.read_bytes())

    def test_drift_is_safe_error(self) -> None:
        with TemporaryDirectory() as td:
            scripts_root = Path(td) / "scripts"
            layers = scripts_root / "layers"
            core = layers / "layer_0_core"
            layers.mkdir(parents=True)
            (layers / "__init__.py").write_text("", encoding="utf-8")
            core.mkdir(parents=True)
            (core / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_0").mkdir(parents=True)
            (core / "level_1").mkdir(parents=True)
            (core / "level_0" / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_1" / "__init__.py").write_text("", encoding="utf-8")
            (core / "level_0" / "__init__.py").write_text(
                "from .submod import exported\n__all__ = ('exported',)\n",
                encoding="utf-8",
            )
            (core / "level_0" / "submod.py").write_text("exported = 1\n", encoding="utf-8")
            target = core / "level_1" / "a.py"
            target.write_text("from level_0.submod import exported\n", encoding="utf-8")

            ops, _ = build_edit_operations_for_tree(
                root=layers,
                scripts_root=scripts_root,
                opts=FixOptions(include_tests=False, rewrite_relative_in_logic="off"),
            )
            # Mutate file to cause drift
            target.write_text("from level_0.submod import exported  # comment\n", encoding="utf-8")
            _, _, apply_errs = apply_edit_operations(ops, apply=True, max_changes_per_file=25)
            self.assertTrue(apply_errs)


if __name__ == "__main__":
    unittest.main()

