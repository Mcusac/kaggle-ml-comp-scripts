"""Unit tests for the import organizer (top-of-file ordering).

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


_ORG = _load_module_from_path(
    "_import_organizer",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "formatting"
    / "import_organizer.py",
)
_SPAN = _load_module_from_path(
    "_text_span_rewrite_engine",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "fix"
    / "text_span_rewrite_engine.py",
)

build_import_organizer_span_edit = _ORG.build_import_organizer_span_edit
apply_span_edit_operations = _SPAN.apply_span_edit_operations


class TestImportOrganizer(unittest.TestCase):
    def test_preserves_future_and_reorders_import_groups(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "a.py"
            p.write_text(
                '"""Doc."""\n'
                "from __future__ import annotations\n"
                "\n"
                "from level_10 import z\n"
                "import os\n"
                "from typing import Any\n"
                "from level_2 import a\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )

            res = build_import_organizer_span_edit(p)
            self.assertIsNotNone(res.op)
            results, summary, errs = apply_span_edit_operations(
                [res.op], apply=True, max_changes_per_file=5
            )
            self.assertFalse(errs)
            self.assertEqual(summary.files_changed, 1)
            out = p.read_text(encoding="utf-8")
            self.assertIn("from __future__ import annotations\n\n", out)
            # Group 1 before group 2, then levels group.
            self.assertLess(out.index("import os"), out.index("from typing import Any"))
            self.assertLess(out.index("from typing import Any"), out.index("from level_2 import a"))
            # numeric-aware: level_2 before level_10
            self.assertLess(out.index("from level_2 import a"), out.index("from level_10 import z"))

    def test_attaches_leading_comment_to_import(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "a.py"
            p.write_text(
                "# keep-with-typing\n"
                "from typing import Any\n"
                "import os\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )
            res = build_import_organizer_span_edit(p)
            self.assertIsNotNone(res.op)
            apply_span_edit_operations([res.op], apply=True, max_changes_per_file=5)
            out = p.read_text(encoding="utf-8")
            # The comment should stay directly above the typing import, and both should now come after `import os`.
            self.assertLess(out.index("import os"), out.index("# keep-with-typing"))
            self.assertLess(out.index("# keep-with-typing"), out.index("from typing import Any"))

    def test_multiline_from_import_is_kept_as_block(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "a.py"
            p.write_text(
                "from typing import (\n"
                "    Any,\n"
                "    Dict,\n"
                ")\n"
                "import os\n"
                "\n"
                "x = 1\n",
                encoding="utf-8",
            )
            res = build_import_organizer_span_edit(p)
            self.assertIsNotNone(res.op)
            apply_span_edit_operations([res.op], apply=True, max_changes_per_file=5)
            out = p.read_text(encoding="utf-8")
            self.assertLess(out.index("import os"), out.index("from typing import ("))
            self.assertIn("    Dict,", out)

    def test_skips_on_tokenize_error(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "a.py"
            p.write_text(
                "import os\n"
                "from typing import (\n"
                "x = 1\n",
                encoding="utf-8",
            )
            res = build_import_organizer_span_edit(p)
            self.assertIsNone(res.op)
            # warnings are allowed; behavior is safe skip


if __name__ == "__main__":
    unittest.main()

