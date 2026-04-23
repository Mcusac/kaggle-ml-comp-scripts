"""Config model for dead symbol detection tooling."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DeadSymbolConfig:
    """
    Configuration for dead symbol detection.

    Fields are intentionally minimal and stable for v1.
    """

    allow_symbol_ids: frozenset[str]
    allow_modules: frozenset[str]
    entrypoint_symbol_ids: frozenset[str]

    @staticmethod
    def default() -> "DeadSymbolConfig":
        return DeadSymbolConfig(
            allow_symbol_ids=frozenset(),
            allow_modules=frozenset(),
            entrypoint_symbol_ids=frozenset(),
        )

    @staticmethod
    def load(path: Path | None) -> "DeadSymbolConfig":
        if path is None:
            return DeadSymbolConfig.default()

        data = json.loads(path.read_text(encoding="utf-8"))
        allow_symbol_ids = frozenset(str(x) for x in data.get("allow_symbol_ids", []) if str(x))
        allow_modules = frozenset(str(x) for x in data.get("allow_modules", []) if str(x))
        entrypoint_symbol_ids = frozenset(
            str(x) for x in data.get("entrypoint_symbol_ids", []) if str(x)
        )
        return DeadSymbolConfig(
            allow_symbol_ids=allow_symbol_ids,
            allow_modules=allow_modules,
            entrypoint_symbol_ids=entrypoint_symbol_ids,
        )

