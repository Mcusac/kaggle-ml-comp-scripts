"""Atomic regex patterns for import and level-path parsing."""

from __future__ import annotations

import re

LEVEL_DIR_RE = re.compile(r"^level_(\d+)$")
DEEP_LEVEL_RE = re.compile(r"^level_(\d+)\.")

CONTEST_LAYER_IMPORT_RE = re.compile(
    r"^layers\.layer_1_competition\.level_1_impl\.([a-zA-Z_][a-zA-Z0-9_]*)\.level_(\d+)(?:\.(.+))?$"
)
INFRA_LAYER_IMPORT_RE = re.compile(
    r"^layers\.layer_1_competition\.level_0_infra\.level_(\d+)(?:\.(.+))?$"
)

__all__ = [
    "LEVEL_DIR_RE",
    "DEEP_LEVEL_RE",
    "CONTEST_LAYER_IMPORT_RE",
    "INFRA_LAYER_IMPORT_RE",
]
