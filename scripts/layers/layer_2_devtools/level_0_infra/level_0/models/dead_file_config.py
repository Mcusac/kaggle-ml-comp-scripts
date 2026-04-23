"""Config model for dead file detection tooling."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DeadFileConfig:
    """
    Configuration for dead file detection.

    Fields are intentionally minimal and stable for v1.
    """

    entrypoint_modules: frozenset[str]
    allow_modules: frozenset[str]
    allow_module_prefixes: tuple[str, ...]

    @staticmethod
    def default() -> "DeadFileConfig":
        return DeadFileConfig(
            entrypoint_modules=frozenset(),
            allow_modules=frozenset(),
            allow_module_prefixes=(),
        )

    def is_allowed(self, module: str) -> bool:
        if not module:
            return True
        if module in self.allow_modules:
            return True
        return any(module.startswith(pfx) for pfx in self.allow_module_prefixes)

    @staticmethod
    def load(path: Path | None) -> "DeadFileConfig":
        if path is None:
            return DeadFileConfig.default()

        data = json.loads(path.read_text(encoding="utf-8"))

        entrypoint_modules = frozenset(
            str(x) for x in data.get("entrypoint_modules", []) if str(x)
        )
        allow_modules = frozenset(str(x) for x in data.get("allow_modules", []) if str(x))
        allow_module_prefixes = tuple(
            str(x) for x in data.get("allow_module_prefixes", []) if str(x)
        )
        return DeadFileConfig(
            entrypoint_modules=entrypoint_modules,
            allow_modules=allow_modules,
            allow_module_prefixes=allow_module_prefixes,
        )

