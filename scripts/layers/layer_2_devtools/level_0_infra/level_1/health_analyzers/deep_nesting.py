"""Directory nesting analyzer (folders containing Python source)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    SKIP_DIRS,
    collect_python_files,
)


class DeepNestingAnalyzer(BaseAnalyzer):
    """
    Analyze directory nesting for code-containing folders.

    “Directory depth” is computed relative to the analyzer root and only considers
    directories that contain at least one ``.py`` file (directly in that folder).
    """

    @property
    def name(self) -> str:
        return "deep_nesting"

    def analyze(self) -> dict[str, Any]:
        files = collect_python_files(self.root)

        dir_to_files: Counter[Path] = Counter()
        for fp in files:
            parent = fp.parent
            if self._should_skip_dir(parent):
                continue
            dir_to_files[parent] += 1

        deep_dirs: list[dict[str, Any]] = []
        hist: Counter[int] = Counter()
        max_depth = 0

        for d, py_files in dir_to_files.items():
            try:
                rel = d.relative_to(self.root)
            except ValueError:
                # Should not happen, but keep analysis resilient.
                continue
            depth = len(rel.parts)
            max_depth = max(max_depth, depth)
            hist[depth] += 1
            deep_dirs.append(
                {
                    "dir": rel.as_posix(),
                    "depth": depth,
                    "py_files": int(py_files),
                }
            )

        deep_dirs.sort(key=lambda r: (r["depth"], r["py_files"], r["dir"]), reverse=True)

        return {
            "max_depth": int(max_depth),
            "deep_dirs": deep_dirs,
            "dir_depth_histogram": {str(k): int(v) for k, v in sorted(hist.items())},
        }

    def _should_skip_dir(self, path: Path) -> bool:
        parts = set(path.parts)
        if SKIP_DIRS & parts:
            return True
        # Extra local skips (not in SKIP_DIRS to avoid affecting other analyzers).
        extra = {".cursor", ".ruff_cache", ".mypy_cache", ".pytest_cache"}
        return bool(extra & parts)
