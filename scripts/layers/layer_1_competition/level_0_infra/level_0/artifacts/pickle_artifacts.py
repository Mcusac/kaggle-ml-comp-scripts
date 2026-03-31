"""Pickle artifact helpers (thin wrappers around core pickle IO)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_4 import PICKLE_HIGHEST_PROTOCOL, load_pickle, save_pickle


def save_pickle_artifact(obj: Any, path: str | Path, *, protocol: int = PICKLE_HIGHEST_PROTOCOL) -> None:
    save_pickle(obj, Path(path), protocol=protocol)


def load_pickle_artifact(path: str | Path) -> Any:
    return load_pickle(Path(path))


__all__ = ["load_pickle_artifact", "save_pickle_artifact"]

