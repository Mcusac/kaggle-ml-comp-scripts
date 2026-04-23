"""Model management helper for per-ontology training."""

import numpy as np
import pickle

from typing import Dict, Any
from pathlib import Path

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_7 import create_tabular_model

_logger = get_logger(__name__)


def _create_placeholder_model(output_dim: int) -> Any:
    """Create a placeholder model when tabular models are unavailable."""
    class PlaceholderModel:
        def fit(self, X, y):
            pass

        def predict(self, X):
            return np.zeros((X.shape[0], output_dim))

    return PlaceholderModel()


class OntologyModelManager:
    """Helper class for creating, training, and saving ontology models."""

    def create_model(
        self,
        ontology: str,
        ontology_config: Dict[str, Any],
        input_dim: int,
        output_dim: int
    ) -> Any:
        """
        Create model for ontology with ontology-specific hyperparameters.

        Uses ``level_7.create_tabular_model``. If that stack is not installed,
        ``ImportError`` is caught and a placeholder model is returned. Other
        errors (e.g. invalid ``model_type`` or hyperparameters) are not
        converted to a placeholder and propagate to the caller.

        Args:
            ontology: Ontology code
            ontology_config: Ontology-specific configuration
            input_dim: Input feature dimension
            output_dim: Output target dimension

        Returns:
            Model instance
        """
        model_type = ontology_config.get('model_type', 'mlp')
        hyperparams = ontology_config.get('model_hyperparameters', {})

        try:
            return create_tabular_model(
                model_type=model_type,
                input_dim=input_dim,
                output_dim=output_dim,
                **hyperparams
            )
        except ImportError:
            _logger.warning("Tabular models not available, using placeholder")
            return _create_placeholder_model(output_dim)
    
    def train_model(
        self,
        model: Any,
        X_train: np.ndarray,
        y_train: np.ndarray,
        ontology_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Train model on training data.

        Args:
            model: Model instance
            X_train: Training features
            y_train: Training targets
            ontology_config: Ontology-specific configuration

        Returns:
            Dictionary of training metrics
        """
        try:
            if hasattr(model, 'fit'):
                model.fit(X_train, y_train, **ontology_config.get('fit_kwargs', {}))
            else:
                _logger.warning("Model does not have fit method")

            return {
                'training_samples': X_train.shape[0],
                'num_targets': y_train.shape[1] if y_train.ndim > 1 else 1
            }
        except Exception as e:
            _logger.error(f"Error training model: {e}")
            return {'error': str(e)}
    
    def save_model(self, model: Any, ontology: str, paths: Any) -> Path:
        """
        Save trained model for ontology.
        
        Args:
            model: Trained model instance
            ontology: Ontology code
            paths: Contest paths instance
            
        Returns:
            Path to saved model
        """
        try:
            models_dir = paths.get_models_dir() if hasattr(paths, 'get_models_dir') else Path('models')
            ontology_model_dir = models_dir / f'{ontology}_ontology'
            ontology_model_dir.mkdir(parents=True, exist_ok=True)
            
            model_path = ontology_model_dir / 'model.pkl'
            
            if hasattr(model, 'save'):
                model.save(str(model_path))
            else:
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            
            _logger.info(f"Saved {ontology} model to {model_path}")
            return model_path
        except Exception as e:
            _logger.error(f"Error saving model for {ontology}: {e}")
            raise
