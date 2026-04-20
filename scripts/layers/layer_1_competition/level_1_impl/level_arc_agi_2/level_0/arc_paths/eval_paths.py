"""Contest JSON filename fallbacks (evaluation split, etc.)."""

from pathlib import Path


def arc_find_first_existing_file(root: Path, names: list[str]) -> Path | None:
    """Return ``root / name`` for the first ``name`` that exists as a file."""
    for name in names:
        p = root / name
        if p.is_file():
            return p
    return None
