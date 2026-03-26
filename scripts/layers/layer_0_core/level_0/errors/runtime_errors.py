"""Runtime-level exceptions.

Do not use CoreRuntimeError for torch/CUDA failures; use the built-in
RuntimeError for those. Use CoreRuntimeError for framework-level runtime failures.
"""


class CoreRuntimeError(Exception):
    """Framework-level runtime failure (e.g. invalid seed). Not for torch/CUDA."""
    pass


class DeviceError(Exception):
    """Device detection or configuration failed."""
    pass


class EnvironmentConfigError(Exception):
    """Environment detection or configuration failed (e.g. unknown purpose)."""
    pass


class ProcessError(Exception):
    """Subprocess execution failed."""
    pass


class ExecutionError(RuntimeError):
    """Execution or dispatch failed. Subclasses built-in RuntimeError."""
    pass
