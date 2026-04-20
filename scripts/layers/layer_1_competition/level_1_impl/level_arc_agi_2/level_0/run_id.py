"""Run-id generation helpers for ARC-AGI-2 run folders."""

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_stage_slug(stage: str) -> str:
    raw = (stage or "").strip().lower()
    return "".join(ch if (ch.isalnum() or ch in ("+", "_", "-")) else "_" for ch in raw) or "unknown"


def generate_run_id(stage: str, seed: int) -> str:
    """Generate a sortable run id. Includes stage + seed for quick scanning."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}_{_safe_stage_slug(stage)}_seed{int(seed)}"
