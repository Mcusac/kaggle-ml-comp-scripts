#!/usr/bin/env python3
"""
Deterministic `__init__.py` regeneration for package trees (relative-only exports).

This tool is meant to be run after file migrations / architecture changes so `__init__.py`
files remain consistent and do not become a maintenance bottleneck.

Important policy:
- Generated output is relative-only. If an existing `__init__.py` contains non-relative
  imports (e.g. `import x` or `from layers... import ...`), treat that as an architectural
  smell and refactor the callers to import from the lowest appropriate module instead.
  Use `--report-nonlocal` to find those files before enabling `--check` in CI.
"""

import argparse
import io
import sys
from pathlib import Path
import importlib.util

_SCRIPT_DIR = Path(__file__).resolve().parent

def _prepend_scripts_root_to_syspath() -> None:
    """
    Ensure the `scripts/` directory (the one that contains `layers/`) is on sys.path.

    Some shells (Git Bash/MSYS) can behave differently with cwd/launch paths, so we
    locate `scripts/` by walking upward from this file.
    """
    for parent in [_SCRIPT_DIR, *_SCRIPT_DIR.parents]:
        if (parent / "layers").is_dir():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            layers_dir = parent / "layers"
            if str(layers_dir) not in sys.path:
                sys.path.insert(0, str(layers_dir))
            return

    # Fallback: allow running from within scripts/ without relying on __file__ depth.
    cwd = Path.cwd().resolve()
    layers_dir = cwd / "layers"
    if layers_dir.is_dir():
        if str(cwd) not in sys.path:
            sys.path.insert(0, str(cwd))
        if str(layers_dir) not in sys.path:
            sys.path.insert(0, str(layers_dir))


_prepend_scripts_root_to_syspath()

def _load_regenerate_inits():
    """
    Load `regenerate_inits` without importing `layers` / barrel `__init__.py` trees.

    We import the `regenerate_inits/` package directly from disk so optional deps in
    unrelated parts of the framework don't prevent devtools from running.
    """
    pkg_dir = (_SCRIPT_DIR.parent / "level_0" / "regenerate_inits").resolve()
    init_path = pkg_dir / "__init__.py"
    if not init_path.exists():
        raise FileNotFoundError(f"regenerate_inits __init__.py not found: {init_path}")

    pkg_name = "_kaggle_ml_regenerate_inits"
    spec = importlib.util.spec_from_file_location(
        pkg_name,
        init_path,
        submodule_search_locations=[str(pkg_dir)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to create module spec for {init_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[pkg_name] = module
    spec.loader.exec_module(module)
    return module


_regen = _load_regenerate_inits()
apply_regeneration = _regen.apply_regeneration
check_regeneration = _regen.check_regeneration
report_nonlocal_imports = _regen.report_nonlocal_imports
DEFAULT_EXCLUDED_SYMBOLS = _regen.DEFAULT_EXCLUDED_SYMBOLS


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main(argv: list[str]) -> int:
    _win_utf8_stdio()

    p = argparse.ArgumentParser(description="Regenerate __init__.py files deterministically.")
    p.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory to scan (e.g. scripts/layers/layer_1_competition/level_1_impl).",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fix", action="store_true", help="Write regenerated __init__.py files.")
    mode.add_argument("--check", action="store_true", help="Exit non-zero if drift is detected.")
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute drift and print diffs; do not modify files.",
    )
    p.add_argument(
        "--include-tests",
        action="store_true",
        help="Include `tests/` directories (default: off).",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-file details (diffs and/or paths).",
    )
    p.add_argument(
        "--report-nonlocal",
        action="store_true",
        help="Report __init__.py files containing non-relative imports.",
    )
    p.add_argument(
        "--exclude-symbol",
        action="append",
        default=[],
        help="Exclude a symbol from leaf-module export inference. Repeatable.",
    )
    p.add_argument(
        "--include-symbol",
        action="append",
        default=[],
        help="Force-include a symbol by removing it from the default excludes. Repeatable.",
    )

    args = p.parse_args(argv)
    root = args.root.resolve()
    if not root.exists():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2

    include_symbols = {s for s in args.include_symbol if s}
    exclude_symbols = set(DEFAULT_EXCLUDED_SYMBOLS)
    exclude_symbols -= include_symbols
    exclude_symbols |= {s for s in args.exclude_symbol if s}
    exclude_symbols_param = None if exclude_symbols == set(DEFAULT_EXCLUDED_SYMBOLS) else exclude_symbols

    if args.report_nonlocal:
        hits = report_nonlocal_imports(root, include_tests=bool(args.include_tests))
        if hits:
            print("Found __init__.py files with non-relative imports:")
            for hp in hits:
                print(str(hp))
            return 1 if args.check else 0
        if args.verbose:
            print("No non-relative imports found in __init__.py files.")

    if args.check:
        rc, drifts = check_regeneration(
            root,
            include_tests=bool(args.include_tests),
            exclude_symbols=exclude_symbols_param,
        )
        if drifts and args.verbose:
            for d in drifts:
                print(str(d.init_path))
        return int(rc)

    if args.dry_run:
        rc, drifts = apply_regeneration(
            root,
            include_tests=bool(args.include_tests),
            dry_run=True,
            exclude_symbols=exclude_symbols_param,
        )
        if drifts:
            for d in drifts:
                if args.verbose:
                    diff = d.unified_diff()
                    if diff:
                        print(diff)
                        print()
                else:
                    print(str(d.init_path))
        return int(rc)

    rc, drifts = apply_regeneration(
        root,
        include_tests=bool(args.include_tests),
        dry_run=False,
        exclude_symbols=exclude_symbols_param,
    )
    if args.verbose:
        for d in drifts:
            print(str(d.init_path))
    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

