"""Stream subprocess stdout/stderr to the notebook with bounded memory."""

import subprocess
from collections import deque

from typing import List, Optional, Tuple


def run_cli_streaming(
    cmd: List[str],
    *,
    description: Optional[str] = None,
    keep_last_n: int = 200,
) -> Tuple[int, List[str]]:
    """Run ``cmd``, print merged stdout/stderr line-by-line, keep last ``keep_last_n`` lines.

    Returns:
        ``(returncode, last_n_lines)`` for failure summaries.
    """
    if description:
        print(f"🚀 {description}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    lines: deque[str] = deque(maxlen=keep_last_n)
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="", flush=True)
        lines.append(line.rstrip())
    returncode = proc.wait()
    return returncode, list(lines)
