"""Multi-Layer Perceptron (MLP) model for tabular data. Uses level_0, level_1, level_2, level_5."""

import numpy as np

from pathlib import Path
from typing import Any, Optional, Tuple
from scipy.sparse import csr_matrix, issparse

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import TabularDataset, get_device
from layers.layer_0_core.level_2 import run_train_epoch, run_validate_epoch, validate_array
from layers.layer_0_core.level_5 import BaseTabularModel, SparseTabularDataset

_logger = get_logger(__name__)
_torch = get_torch()
_nn = _torch.nn
_optim = _torch.optim
_DataLoader = _torch.utils.data.DataLoader


def _create_training_datasets(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    output_dim: int,
    sparse_loss_class: Optional[Any] = None,
) -> Tuple[Any, Any, Any]:
    """
    Create train/val datasets and criterion for MLP training.
    Uses SparseTabularDataset + sparse_loss when output_dim > 10000 and sparse_loss_class provided.
    """
    if output_dim > 10000 and sparse_loss_class is not None:
        y_train_sp = y_train if issparse(y_train) else csr_matrix(y_train)
        y_val_sp = y_val if issparse(y_val) else csr_matrix(y_val)
        train_dataset = SparseTabularDataset(X_train, y_train_sp)
        val_dataset = SparseTabularDataset(X_val, y_val_sp)
        criterion = sparse_loss_class()
    else:
        train_dataset = TabularDataset(X_train, y_train)
        val_dataset = TabularDataset(X_val, y_val)
        criterion = _nn.BCEWithLogitsLoss()
    return train_dataset, val_dataset, criterion


class _MLPNetwork(_nn.Module):
    """Multi-Layer Perceptron network architecture."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dims: list = None,
        dropout_rate: float = 0.3,
        use_batch_norm: bool = True,
    ):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [512, 256]
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(_nn.Linear(prev_dim, hidden_dim))
            if use_batch_norm:
                layers.append(_nn.BatchNorm1d(hidden_dim))
            layers.append(_nn.ReLU())
            layers.append(_nn.Dropout(dropout_rate))
            prev_dim = hidden_dim
        layers.append(_nn.Linear(prev_dim, output_dim))
        self.network = _nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class MLPModel(BaseTabularModel):
    """
    Multi-Layer Perceptron (MLP) model for multi-label classification.

    PyTorch-based neural network with configurable architecture.
    Supports GPU acceleration and sparse label handling.

    Supports sparse tensor architecture for large label spaces (16K+ labels).
    Automatically uses sparse dataset and loss when output_dim > 10000.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dims: list = None,
        dropout_rate: float = 0.3,
        learning_rate: float = 1e-3,
        batch_size: int = 32,
        num_epochs: int = 10,
        use_batch_norm: bool = True,
        device: str = "auto",
        sparse_loss_class=None,
        **kwargs,
    ):
        if hidden_dims is None:
            hidden_dims = [512, 256]
        super().__init__(model_type="nn", **kwargs)
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dims = hidden_dims
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.use_batch_norm = use_batch_norm
        self.device_str = device
        self.sparse_loss_class = sparse_loss_class
        self.device = get_device(device)
        self.model = _MLPNetwork(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            dropout_rate=dropout_rate,
            use_batch_norm=use_batch_norm,
        ).to(self.device)
        self.optimizer = None
        self.criterion = None

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.1,
        **kwargs,
    ) -> "MLPModel":
        """Train the MLP model."""
        del kwargs
        _logger.info("Training MLP model...")
        _logger.info("  Input shape: %s, Target shape: %s", X.shape, y.shape)
        _logger.info("  Device: %s", self.device)
        validate_array(X, expected_shape=(None, self.input_dim), name="X")
        validate_array(y, expected_shape=(None, self.output_dim), name="y")
        self.optimizer = _optim.Adam(
            self.model.parameters(), lr=self.learning_rate
        )
        self.criterion = _nn.BCEWithLogitsLoss()
        n_train = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:n_train], X[n_train:]
        y_train, y_val = y[:n_train], y[n_train:]
        train_dataset, val_dataset, self.criterion = _create_training_datasets(
            X_train, y_train, X_val, y_val, self.output_dim,
            sparse_loss_class=self.sparse_loss_class,
        )
        train_loader = _DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True
        )
        val_loader = _DataLoader(
            val_dataset, batch_size=self.batch_size, shuffle=False
        )
        for epoch in range(self.num_epochs):
            avg_train_loss = run_train_epoch(
                self.model, train_loader, self.optimizer,
                self.criterion, self.device,
            )
            avg_val_loss = run_validate_epoch(
                self.model, val_loader, self.criterion, self.device,
            )
            if (epoch + 1) % max(1, self.num_epochs // 10) == 0:
                _logger.info(
                    "  Epoch %s/%s - Train Loss: %.4f, Val Loss: %.4f",
                    epoch + 1, self.num_epochs, avg_train_loss, avg_val_loss,
                )
        self.is_fitted = True
        _logger.info("MLP training complete")
        return self

    def predict(
        self, X: np.ndarray, threshold: float = 0.5, **kwargs
    ) -> np.ndarray:
        """Generate binary predictions."""
        del kwargs
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Generate probability predictions."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        self.model.eval()
        dataset = TabularDataset(X)
        dataloader = _DataLoader(
            dataset, batch_size=self.batch_size, shuffle=False
        )
        all_probs = []
        with _torch.no_grad():
            for batch_X, _ in dataloader:
                batch_X = batch_X.to(self.device)
                logits = self.model(batch_X)
                probs = _torch.sigmoid(logits)
                all_probs.append(probs.cpu().numpy())
        return np.concatenate(all_probs, axis=0)

    def save(self, path: str) -> None:
        """Save model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        _torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "input_dim": self.input_dim,
                "output_dim": self.output_dim,
                "hidden_dims": self.hidden_dims,
                "dropout_rate": self.dropout_rate,
                "learning_rate": self.learning_rate,
                "batch_size": self.batch_size,
                "num_epochs": self.num_epochs,
                "use_batch_norm": self.use_batch_norm,
                "device_str": self.device_str,
                "is_fitted": self.is_fitted,
            },
            path,
        )
        _logger.info("Saved MLP model to %s", path)

    def load(self, path: str) -> "MLPModel":
        """Load model from disk."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        checkpoint = _torch.load(path, map_location=self.device)
        self.input_dim = checkpoint["input_dim"]
        self.output_dim = checkpoint["output_dim"]
        self.hidden_dims = checkpoint["hidden_dims"]
        self.dropout_rate = checkpoint["dropout_rate"]
        self.learning_rate = checkpoint["learning_rate"]
        self.batch_size = checkpoint["batch_size"]
        self.num_epochs = checkpoint["num_epochs"]
        self.use_batch_norm = checkpoint["use_batch_norm"]
        self.device_str = checkpoint["device_str"]
        self.is_fitted = checkpoint["is_fitted"]
        self.model = _MLPNetwork(
            input_dim=self.input_dim,
            output_dim=self.output_dim,
            hidden_dims=self.hidden_dims,
            dropout_rate=self.dropout_rate,
            use_batch_norm=self.use_batch_norm,
        ).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        _logger.info("Loaded MLP model from %s", path)
        return self
