"""Unit tests for unused import cleanup span edits.

Uses `unittest` to avoid importing repo-level pytest configuration.
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


_CLEAN = _load_module_from_path(
    "_unused_import_cleanup",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "fix"
    / "unused_import_cleanup.py",
)


class TestUnusedImportCleanup(unittest.TestCase):
    def test_removes_from_import_name_and_keeps_rest(self) -> None:
        stmt = "from typing import Any, Dict, Optional\n"
        out = _CLEAN._render_import_stmt_after_removal(stmt, {"Dict"})
        self.assertIsNotNone(out)
        new_stmt, removed = out  # type: ignore[misc]
        self.assertEqual(removed, 1)
        self.assertEqual(new_stmt, "from typing import Any, Optional\n")

    def test_removes_from_import_and_preserves_attached_comment(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "a.py"
            p.write_text(
                "# attached\n"
                "from typing import Any, Dict\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )
            op, removed, warnings = _CLEAN._build_unused_import_cleanup_span_edit(
                path=p, unused_names={"Dict"}
            )
            self.assertFalse(warnings)
            self.assertIsNotNone(op)
            self.assertEqual(removed, 1)
            self.assertIn("# attached\nfrom typing import Any\n", op.new_text)  # type: ignore[union-attr]

    def test_removes_import_alias_by_asname(self) -> None:
        stmt = "import numpy as np\n"
        out = _CLEAN._render_import_stmt_after_removal(stmt, {"np"})
        self.assertIsNotNone(out)
        new_stmt, removed = out  # type: ignore[misc]
        self.assertEqual(removed, 1)
        self.assertEqual(new_stmt, "")

    def test_removes_name_from_multi_import(self) -> None:
        stmt = "import os, sys\n"
        out = _CLEAN._render_import_stmt_after_removal(stmt, {"sys"})
        self.assertIsNotNone(out)
        new_stmt, removed = out  # type: ignore[misc]
        self.assertEqual(removed, 1)
        self.assertEqual(new_stmt, "import os\n")

    def test_noqa_skips_rewrite(self) -> None:
        stmt = "from typing import Any  # noqa: F401\n"
        out = _CLEAN._render_import_stmt_after_removal(stmt, {"Any"})
        self.assertIsNone(out)

    def test_builds_span_edit_for_multiline_parenthesized_from_import(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "a.py"
            p.write_text(
                '"""Doc."""\n'
                "from __future__ import annotations\n"
                "\n"
                "from typing import (\n"
                "    Any,\n"
                "    Dict,\n"
                "    Optional,\n"
                ")\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )
            op, removed, warnings = _CLEAN._build_unused_import_cleanup_span_edit(
                path=p, unused_names={"Dict"}
            )
            self.assertFalse(warnings)
            self.assertIsNotNone(op)
            self.assertEqual(removed, 1)
            self.assertIn("from typing import Any, Optional\n", op.new_text)  # type: ignore[union-attr]
            self.assertNotIn("Dict", op.new_text)  # type: ignore[union-attr]


if __name__ == "__main__":
    unittest.main()

