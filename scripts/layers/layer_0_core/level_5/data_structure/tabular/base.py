"""Base tabular model abstract class. Uses level_0 and level_4 save/load pickle."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np

from layers.layer_0_core.level_0 import ensure_file_dir, get_logger
from layers.layer_0_core.level_4 import load_pickle, save_pickle

_logger = get_logger(__name__)


class BaseTabularModel(ABC):
    """
    Abstract base class for tabular models.
    
    All tabular models (tree-based, linear, neural networks) should inherit
    from this class to ensure consistent interface across model types.
    """
    
    def __init__(self, model_type: str, **kwargs):
        """
        Initialize base tabular model.
        
        Args:
            model_type: Type of model ('linear', 'tree', 'nn').
            **kwargs: Model-specific initialization parameters.
        """
        self.model_type = model_type
        self.model = None
        self.is_fitted = False
    
    @abstractmethod
    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> 'BaseTabularModel':
        """
        Train the model.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features).
            y: Target matrix of shape (n_samples, n_targets) for multi-label,
               or (n_samples,) for single-label.
            **kwargs: Additional training parameters (validation data, callbacks, etc.).
            
        Returns:
            Self for method chaining.
        """
        ...
    
    def predict(self, X: np.ndarray, threshold: float = 0.5, **kwargs) -> np.ndarray:
        """
        Generate binary predictions using threshold on predict_proba.
        Default implementation for sklearn-based models. Override if custom logic needed.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features).
            threshold: Probability threshold for binary classification (default: 0.5).
            **kwargs: Additional prediction parameters.
            
        Returns:
            Binary predictions array of shape (n_samples, n_targets).
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Generate probability predictions.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features).
            
        Returns:
            Probability array of shape (n_samples, n_targets).
        """
        ...
    
    @abstractmethod
    def save(self, path: str) -> None:
        """
        Save model to disk.
        
        Args:
            path: Path to save the model.
        """
        ...
    
    @abstractmethod
    def load(self, path: str) -> 'BaseTabularModel':
        """
        Load model from disk.
        
        Args:
            path: Path to load the model from.
            
        Returns:
            Self for method chaining.
        """
        ...
    
    def _save_with_pickle(
        self,
        path: str,
        model_data: Dict[str, Any],
        model_name: str
    ) -> None:
        """Helper for pickle-based model persistence. Uses level_4 save_pickle."""
        ensure_file_dir(path)
        save_pickle(model_data, path)
        _logger.info(f"✅ Saved {model_name} model to {path}")

    def _load_from_pickle(self, path: str, model_name: str) -> Dict[str, Any]:
        """Helper for pickle-based model loading. Uses level_4 load_pickle."""
        data = load_pickle(path)
        _logger.info(f"✅ Loaded {model_name} model from {path}")
        return data

    def get_params(self) -> Dict[str, Any]:
        """
        Get model hyperparameters.
        
        Returns:
            Dictionary of hyperparameters.
        """
        if hasattr(self.model, 'get_params'):
            return self.model.get_params()
        return {}
    
    def set_params(self, **params) -> 'BaseTabularModel':
        """
        Set model hyperparameters.
        
        Args:
            **params: Hyperparameters to set.
            
        Returns:
            Self for method chaining.
        """
        if hasattr(self.model, 'set_params'):
            self.model.set_params(**params)
        return self
