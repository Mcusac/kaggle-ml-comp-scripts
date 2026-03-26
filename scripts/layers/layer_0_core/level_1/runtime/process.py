"""Subprocess execution utilities.

Pure process execution without logging or printing side effects.
"""

import subprocess

from typing import List, Optional

from layers.layer_0_core.level_0 import ProcessResult, validate_command


def run_command(
    cmd: List[str],
    check: bool = True,
    timeout: Optional[int] = None,
) -> ProcessResult:
    """
    Execute a command.

    Args:
        cmd: Command as list of strings
        check: Raise CalledProcessError on failure
        timeout: Optional timeout in seconds

    Returns:
        ProcessResult
    """
    validate_command(cmd)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check,
        timeout=timeout,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }