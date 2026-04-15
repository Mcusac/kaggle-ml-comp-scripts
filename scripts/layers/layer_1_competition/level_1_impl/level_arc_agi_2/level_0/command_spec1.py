"""Command specification for ARC-AGI-2 contest CLI commands."""

from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class CommandSpec:
    name: str
    help: str
    builder: Callable[[Any], None]