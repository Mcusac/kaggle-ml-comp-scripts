"""Contest-agnostic model registry. Contest layer registers model factories on import."""

from typing import Any, Callable, Dict


class ModelRegistry:
    """
    Registry for model creation functions. Contest implementations register their models.
    
    Warning: _registry is a class-level variable shared across all callers
    and test runs. Tests that register model types must clean up after
    themselves (e.g. `del ModelRegistry._registry[key]`) to avoid order-dependent failures.
    """

    _registry: Dict[str, Callable[..., Any]] = {}

    @classmethod
    def register(cls, model_type: str, factory: Callable[..., Any]) -> None:
        """Register a factory for the given model type."""
        cls._registry[model_type] = factory

    @classmethod
    def create(cls, model_type: str, **kwargs: Any) -> Any:
        """Create a model instance by type. Raises ValueError if type not registered."""
        if model_type not in cls._registry:
            raise ValueError(
                f"Unknown model type: {model_type}. Registered: {list(cls._registry.keys())}"
            )
        return cls._registry[model_type](**kwargs)

    @classmethod
    def is_registered(cls, model_type: str) -> bool:
        """Return True if model_type is registered."""
        return model_type in cls._registry
