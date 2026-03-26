"""Small shared contracts for API envelopes (infra; no impl dependency)."""

from .envelope import err
from .envelope import ok
from .envelope import parse_generated
from .envelope import parse_generated_optional

__all__ = ["err", "ok", "parse_generated", "parse_generated_optional"]
