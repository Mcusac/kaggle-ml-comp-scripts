from dataclasses import dataclass
from typing import Callable, Any


Block = Callable[[Any], None]


@dataclass(frozen=True)
class CommandSpec:
    name: str
    help: str
    blocks: list[Block]
    custom: list[Block] | None = None