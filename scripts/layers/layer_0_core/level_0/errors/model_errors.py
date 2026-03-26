"""Model-related exceptions.

Hierarchy:
- ModelError (base)
  - ModelLoadError (model loading failed)
  - ModelTrainingError (training failed)
  - ModelPredictionError (prediction failed)
"""


class ModelError(Exception):
    """Base exception for model errors.

    Raised when model-related operations fail.
    Subclasses provide more specific error categories.
    """
    pass


class ModelLoadError(ModelError):
    """Raised when model cannot be loaded.

    Examples:
    - Model file not found
    - Incompatible model format
    - Missing model architecture
    - Corrupted checkpoint

    Usage:
        >>> if not model_path.exists():
        ...     raise ModelLoadError(f"Model not found: {model_path}")
    """
    pass


class ModelTrainingError(ModelError):
    """Raised when model training fails.

    Examples:
    - Training divergence
    - Out of memory during training
    - Invalid hyperparameters
    - Data/model shape mismatch

    Usage:
        >>> if loss > 1e10:
        ...     raise ModelTrainingError("Training diverged (loss > 1e10)")
    """
    pass


class ModelPredictionError(ModelError):
    """Raised when model prediction fails.

    Examples:
    - Input shape mismatch
    - Invalid input data
    - Model not trained
    - Out of memory during inference

    Usage:
        >>> if X.shape[1] != model.n_features_:
        ...     raise ModelPredictionError(
        ...         f"Expected {model.n_features_} features, got {X.shape[1]}"
        ...     )
    """
    pass
