"""Shared envelope helpers for public API modules (infra-level primitive)."""

from __future__ import annotations

from datetime import date
from typing import Any


def ok(data: dict[str, Any]) -> dict[str, Any]:
    return {"status": "ok", "data": data, "errors": []}


def err(errors: list[str]) -> dict[str, Any]:
    return {"status": "error", "data": {}, "errors": errors}


def parse_generated(raw: Any) -> date:
    """Require a date or ISO date string."""
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        return date.fromisoformat(raw)
    raise ValueError("generated must be a date or YYYY-MM-DD string")


def parse_generated_optional(raw: Any) -> date | None:
    """Date, ISO string, or None for callers that omit timestamp."""
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        return date.fromisoformat(raw)
    raise TypeError("generated must be None, a date, or YYYY-MM-DD string")


__all__ = ["err", "ok", "parse_generated", "parse_generated_optional"]
