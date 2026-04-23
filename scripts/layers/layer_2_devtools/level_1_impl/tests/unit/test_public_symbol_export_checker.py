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


_CHECKER = _load_module_from_path(
    "_public_symbol_export_checker",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "public_symbol_export_checker.py",
)

_compute_findings = _CHECKER._compute_findings


class TestPublicSymbolExportChecker(unittest.TestCase):
    def test_reports_missing_symbol_when_not_exported(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            pkg = root / "pkg"
            pkg.mkdir(parents=True)

            (pkg / "mod.py").write_text(
                "class PublicThing:\n"
                "    pass\n"
                "\n"
                "def public_fn():\n"
                "    return 1\n"
                "\n"
                "def _private():\n"
                "    return 2\n",
                encoding="utf-8",
            )
            (pkg / "__init__.py").write_text(
                '"""Pkg."""\n'
                "from .mod import PublicThing\n"
                "\n"
                "__all__ = [\n"
                '    "PublicThing",\n'
                "]\n",
                encoding="utf-8",
            )

            findings, parse_errs = _compute_findings(root, include_tests=False)
            self.assertEqual(parse_errs, 0)
            f = next(x for x in findings if x.package_dir == pkg)
            self.assertEqual(f.package_dir, pkg)
            self.assertIn("public_fn", f.missing)
            self.assertNotIn("PublicThing", f.missing)
            self.assertNotIn("_private", f.missing)

    def test_no_missing_when_init_matches_expected(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td) / "root"
            pkg = root / "pkg"
            pkg.mkdir(parents=True)

            (pkg / "mod.py").write_text(
                "class PublicThing:\n"
                "    pass\n"
                "\n"
                "def public_fn():\n"
                "    return 1\n",
                encoding="utf-8",
            )
            (pkg / "__init__.py").write_text(
                '"""Pkg."""\n'
                "from .mod import PublicThing, public_fn\n"
                "\n"
                "__all__ = [\n"
                '    "PublicThing",\n'
                '    "public_fn",\n'
                "]\n",
                encoding="utf-8",
            )

            findings, parse_errs = _compute_findings(root, include_tests=False)
            self.assertEqual(parse_errs, 0)
            f = next(x for x in findings if x.package_dir == pkg)
            self.assertEqual(f.missing, [])


if __name__ == "__main__":
    unittest.main()

