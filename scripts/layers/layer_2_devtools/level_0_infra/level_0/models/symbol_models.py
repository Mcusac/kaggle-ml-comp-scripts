"""Models for symbol definition/reference indexing."""

from dataclasses import dataclass
from enum import Enum


class SymbolKind(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    CONSTANT = "constant"


@dataclass(frozen=True, slots=True)
class SymbolDefinition:
    module: str
    qualname: str
    kind: SymbolKind
    file: str
    line_start: int
    line_end: int
    is_public: bool

    @property
    def symbol_id(self) -> str:
        return f"{self.module}:{self.qualname}"

