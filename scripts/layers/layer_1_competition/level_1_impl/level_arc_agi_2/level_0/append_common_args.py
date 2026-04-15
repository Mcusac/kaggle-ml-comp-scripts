"""Shared command utilities."""

from typing import List, Optional

CONTEST = "arc_agi_2"


def append_common_args(
    cmd: List[str],
    run_id: Optional[str],
    run_dir: Optional[str],
    log_file: Optional[str],
) -> None:
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])