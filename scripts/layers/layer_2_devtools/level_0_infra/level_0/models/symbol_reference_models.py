"""Models for symbol reference indexing."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SymbolReference:
    ref_module: str
    ref_file: str
    line: int
    col: int
    resolved_symbol_id: str

