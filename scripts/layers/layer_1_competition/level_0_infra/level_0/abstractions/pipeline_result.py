"""Structured pipeline outcome type shared across contest implementations."""

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class PipelineResult:
    """Structured, program-friendly outcome for a contest pipeline stage."""

    success: bool
    stage: str
    error: str | None = None
    artifacts: Mapping[str, str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def ok(
        *,
        stage: str,
        artifacts: Mapping[str, str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "PipelineResult":
        return PipelineResult(
            success=True,
            stage=str(stage),
            error=None,
            artifacts=dict(artifacts or {}),
            metadata=dict(metadata or {}),
        )

    @staticmethod
    def fail(
        *,
        stage: str,
        error: str,
        artifacts: Mapping[str, str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "PipelineResult":
        return PipelineResult(
            success=False,
            stage=str(stage),
            error=str(error),
            artifacts=dict(artifacts or {}),
            metadata=dict(metadata or {}),
        )
