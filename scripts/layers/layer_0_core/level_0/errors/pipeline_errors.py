"""Pipeline-related errors.

Hierarchy:
- PipelineError (base)
  - PipelineSetupError (pipeline configuration failed)
  - PipelineExecutionError (pipeline runtime failed)
"""


class PipelineError(Exception):
    """Base exception for pipeline errors.

    Raised when pipeline operations fail.
    Subclasses provide more specific error categories.
    """
    pass


class PipelineSetupError(PipelineError):
    """Raised when pipeline setup fails.

    Examples:
    - Invalid pipeline configuration
    - Missing pipeline components
    - Component initialization failures
    - Incompatible component versions

    Usage:
        >>> if not hasattr(config, 'training'):
        ...     raise PipelineSetupError("Config missing training section")
    """
    pass


class PipelineExecutionError(PipelineError):
    """Raised when pipeline execution fails.

    Examples:
    - Step execution failures
    - Component crashes
    - Resource exhaustion
    - Timeout exceeded

    Usage:
        >>> try:
        ...     result = pipeline.run(data)
        ... except Exception as e:
        ...     raise PipelineExecutionError(f"Pipeline failed at step {step}: {e}")
    """
    pass
