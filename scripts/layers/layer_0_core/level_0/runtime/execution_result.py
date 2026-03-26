"""Execution result models."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ExecutionResult:
    """Represents the result of an executed operation."""

    returncode: int
    output: Sequence[str] = ()
    log_file: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0

    @property
    def failed(self) -> bool:
        return not self.succeeded