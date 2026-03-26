"""Execute command and stream output."""

import subprocess
from collections import deque

from typing import List, Optional, Tuple


def validate_command(cmd: List[str]) -> None:
    """
    Validate that cmd is a non-empty list of strings.

    Raises:
        ValueError: If cmd is empty.
        TypeError: If cmd is not a list or contains non-string elements.
    """
    if not cmd:
        raise ValueError("Command list cannot be empty")
    if not isinstance(cmd, list):
        raise TypeError(f"Command must be list, got {type(cmd)}")
    if not all(isinstance(c, str) for c in cmd):
        raise TypeError("All command parts must be strings")


def run_command_stream(
    cmd: List[str],
    timeout: Optional[int] = None,
    keep_last_n: int = 200,
) -> Tuple[int, List[str]]:
    """
    Execute command and stream output.
    Rolling window behaviour is implemented by keeping only the last N lines in memory.

    Returns:
        (return_code, last_n_lines)
    """
    validate_command(cmd)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    lines: deque[str] = deque(maxlen=keep_last_n)

    assert process.stdout is not None

    for line in process.stdout:
        lines.append(line.rstrip())

    returncode = process.wait(timeout=timeout)
    return returncode, list(lines)