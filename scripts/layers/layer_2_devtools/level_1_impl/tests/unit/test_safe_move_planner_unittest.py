"""Unit tests for Safe Move Planner primitives.

Note: uses `unittest` to avoid importing repo-level pytest conftest (may pull heavy deps).
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


_MOVE_PLAN = _load_module_from_path(
    "_safe_move_move_plan",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "moves"
    / "move_plan.py",
)
_MOVE_REWRITE = _load_module_from_path(
    "_safe_move_import_rewriter",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "fix"
    / "move_import_rewriter.py",
)
_SPAN_ENGINE = _load_module_from_path(
    "_import_rewrite_engine",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "fix"
    / "import_rewrite_engine.py",
)

MoveSpec = _MOVE_PLAN.MoveSpec
compute_move_plan = _MOVE_PLAN.compute_move_plan
MoveImportRewrite = _MOVE_REWRITE.MoveImportRewrite
build_move_import_rewrite_ops = _MOVE_REWRITE.build_move_import_rewrite_ops
apply_edit_operations = _SPAN_ENGINE.apply_edit_operations


class TestSafeMovePlanner(unittest.TestCase):
    def test_compute_destination_by_level_segment(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            src = root / "level_1" / "foo" / "bar.py"
            src.parent.mkdir(parents=True)
            src.write_text("x = 1\n", encoding="utf-8")

            plan = compute_move_plan(
                spec=MoveSpec(root=root, src_path=src, dest_level=2),
            )
            self.assertEqual(plan.old_module, "level_1.foo.bar")
            self.assertEqual(plan.new_module, "level_2.foo.bar")
            self.assertEqual(plan.dest_path, root / "level_2" / "foo" / "bar.py")

    def test_move_import_rewriter_handles_multiline_from_import(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            (root / "level_1" / "foo").mkdir(parents=True)
            (root / "level_2" / "foo").mkdir(parents=True)
            (root / "level_1" / "foo" / "__init__.py").write_text("", encoding="utf-8")
            (root / "level_2" / "foo" / "__init__.py").write_text("", encoding="utf-8")
            (root / "level_1" / "foo" / "bar.py").write_text("value = 1\n", encoding="utf-8")

            importer = root / "level_3" / "use_it.py"
            importer.parent.mkdir(parents=True)
            importer.write_text(
                "from level_1.foo import (\n"
                "    bar,\n"
                ")\n"
                "import level_1.foo.bar as b\n",
                encoding="utf-8",
            )

            ops, warnings = build_move_import_rewrite_ops(
                root=root,
                rewrite=MoveImportRewrite(
                    old_module="level_1.foo.bar",
                    new_module="level_2.foo.bar",
                ),
                include_tests=False,
            )
            self.assertFalse(warnings)
            self.assertTrue(ops)

            _, summary, errors = apply_edit_operations(ops, apply=True, max_changes_per_file=25)
            self.assertFalse(errors)
            self.assertEqual(summary.files_changed, 1)
            updated = importer.read_text(encoding="utf-8")
            self.assertIn("from level_2.foo import", updated)
            self.assertIn("import level_2.foo.bar as b", updated)


if __name__ == "__main__":
    unittest.main()

