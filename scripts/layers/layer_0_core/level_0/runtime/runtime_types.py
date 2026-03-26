"""Runtime-level type definitions."""

from typing import TypedDict, List


class ProcessResult(TypedDict):
    """Result from command execution."""
    returncode: int
    stdout: str
    stderr: str


class DeviceInfo(TypedDict):
    """Hardware information."""
    cuda_available: bool
    device_count: int
    device_names: List[str]