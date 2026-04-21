"""Orchestrate `__init__.py` regeneration for a tree."""

from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass
from pathlib import Path

from .public_symbols import public_symbols_from_file
from .render import RenderedInit
from .render import render_aggregate_init
from .render import render_leaf_init
from .render import render_stub_init
from .walk import bottom_up_package_dirs
from .walk import read_package_contents


@dataclass(frozen=True)
class Drift:
    package_dir: Path
    init_path: Path
    expected: str
    actual: str
    kind: str

    def unified_diff(self) -> str:
        return "\n".join(
            difflib.unified_diff(
                self.actual.splitlines(),
                self.expected.splitlines(),
                fromfile=str(self.init_path),
                tofile=str(self.init_path) + " (expected)",
                lineterm="",
            )
        )


def _init_path(package_dir: Path) -> Path:
    return package_dir / "__init__.py"


def expected_init_for_package(package_dir: Path, include_tests: bool) -> RenderedInit:
    contents = read_package_contents(package_dir, include_tests=include_tests)

    if contents.subpackages:
        return render_aggregate_init(contents.subpackages)

    module_to_symbols: dict[str, list[str]] = {}
    for mod in contents.modules:
        path = package_dir / f"{mod}.py"
        syms = public_symbols_from_file(path)
        if syms:
            module_to_symbols[mod] = syms

    if module_to_symbols:
        return render_leaf_init(module_to_symbols)

    return render_stub_init()


def compute_drift(root: Path, include_tests: bool) -> list[Drift]:
    drifts: list[Drift] = []
    for pkg_dir in bottom_up_package_dirs(root, include_tests=include_tests):
        init_path = _init_path(pkg_dir)
        rendered = expected_init_for_package(pkg_dir, include_tests=include_tests)
        expected = rendered.text
        try:
            actual = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
        except OSError:
            actual = ""

        if actual != expected:
            drifts.append(
                Drift(
                    package_dir=pkg_dir,
                    init_path=init_path,
                    expected=expected,
                    actual=actual,
                    kind=rendered.kind,
                )
            )
    return drifts


def check_regeneration(
    root: Path,
    include_tests: bool = False,
) -> tuple[int, list[Drift]]:
    """
    Return (exit_code, drifts).
    Exit code is 0 on no drift, 1 otherwise.
    """
    drifts = compute_drift(root, include_tests=include_tests)
    return (0 if not drifts else 1), drifts


def apply_regeneration(
    root: Path,
    include_tests: bool = False,
    dry_run: bool = False,
) -> tuple[int, list[Drift]]:
    """
    Apply deterministic regeneration under `root`.

    Returns (exit_code, drifts). Exit code is always 0 unless an IO error occurs.
    """
    drifts = compute_drift(root, include_tests=include_tests)
    if dry_run:
        return 0, drifts

    try:
        for d in drifts:
            d.init_path.parent.mkdir(parents=True, exist_ok=True)
            d.init_path.write_text(d.expected, encoding="utf-8")
    except OSError:
        return 1, drifts

    return 0, drifts


def _has_nonlocal_imports(source: str) -> bool:
    """
    Detect `import X` or `from X import ...` where `X` is non-relative.

    Relative imports in `ast.ImportFrom` have `level >= 1`.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return True

    for node in tree.body:
        if isinstance(node, ast.Import):
            return True
        if isinstance(node, ast.ImportFrom):
            if (node.level or 0) == 0:
                return True
    return False


def report_nonlocal_imports(
    root: Path,
    include_tests: bool = False,
) -> list[Path]:
    """
    Return `__init__.py` paths that contain non-relative imports.

    This is intended as a migration aid: those inits should be refactored so callers
    import from the correct lowest-level module instead of cross-level re-exports.
    """
    hits: list[Path] = []
    for pkg_dir in bottom_up_package_dirs(root, include_tests=include_tests):
        init_path = _init_path(pkg_dir)
        if not init_path.exists():
            continue
        try:
            src = init_path.read_text(encoding="utf-8")
        except OSError:
            hits.append(init_path)
            continue
        if _has_nonlocal_imports(src):
            hits.append(init_path)
    return sorted(set(hits), key=lambda p: str(p))

