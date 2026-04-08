"""Locate ``layer_0_core`` directory ancestors."""

from pathlib import Path


def find_layer_0_core_ancestor(start: Path) -> Path | None:
    """Return the nearest ancestor named ``layer_0_core`` if it is a directory."""
    for path in [start, *start.parents]:
        if path.name == "layer_0_core" and path.is_dir():
            return path
    return None


__all__ = ["find_layer_0_core_ancestor"]
