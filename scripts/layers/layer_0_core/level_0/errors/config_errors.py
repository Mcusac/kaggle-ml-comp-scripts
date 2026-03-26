"""Configuration-related exceptions."""


class ConfigError(Exception):
    """Base exception for configuration errors.

    Raised when configuration-related operations fail.
    Subclasses provide more specific error categories.
    """
    pass


class ConfigValidationError(ConfigError):
    """Raised when config validation fails.

    Examples:
    - Missing required config sections
    - Invalid config values (negative batch size, etc.)
    - Type mismatches in config fields

    Usage:
        >>> if config.batch_size <= 0:
        ...     raise ConfigValidationError("batch_size must be positive")
    """
    pass


class ConfigLoadError(ConfigError):
    """Raised when config file cannot be loaded.

    Examples:
    - Config file not found
    - Invalid YAML/JSON syntax
    - File permissions issues

    Usage:
        >>> try:
        ...     config = load_yaml('config.yml')
        ... except Exception as e:
        ...     raise ConfigLoadError(f"Failed to load config: {e}")
    """
    pass
