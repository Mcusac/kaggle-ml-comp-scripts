"""CLI command dispatcher."""

import argparse
from typing import Callable, Dict, Optional


def dispatch_command(
    command: str,
    args: argparse.Namespace,
    primary_handlers: Dict[str, Callable[[argparse.Namespace], None]],
    fallback_handlers: Optional[Dict[str, Callable[[argparse.Namespace], None]]] = None,
) -> None:
    """
    Dispatch command to appropriate handler.

    Primary handlers are tried first; if not found, fallback handlers are tried.

    Args:
        command: Command name. Must be a valid command string.
        args: Parsed arguments object from argparse.
        primary_handlers: Dict of command -> handler (e.g. framework commands).
        fallback_handlers: Optional dict of command -> handler (e.g. contest-specific).

    Raises:
        ValueError: If command is None, empty, or unknown.
        RuntimeError: If pipeline execution fails (propagated from pipeline functions).
    """
    if not command or not isinstance(command, str):
        raise ValueError(f"command must be non-empty string, got {command}")

    handler = primary_handlers.get(command)
    if handler is not None:
        handler(args)
        return

    ch = fallback_handlers or {}
    if command in ch:
        ch[command](args)
        return

    primary = ", ".join(sorted(primary_handlers.keys()))
    extra = f" Fallback commands: {', '.join(sorted(ch.keys()))}." if ch else ""
    raise ValueError(
        f"Unknown command: '{command}'. Primary: {primary}.{extra}"
    )