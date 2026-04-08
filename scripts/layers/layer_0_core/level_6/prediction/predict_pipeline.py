"""Prediction pipeline."""

import numpy as np

from pathlib import Path
from typing import Any, Dict

from level_0 import ensure_dir, get_logger, get_torch
from level_1 import BasePipeline, get_device, validate_config_section_exists
from level_2 import VisionPredictor
from level_3 import TTAPredictor
from level_4 import create_test_dataloader, create_vision_model, load_pickle

logger = get_logger(__name__)
torch = get_torch()


class PredictPipeline(BasePipeline):
    """
    Atomic pipeline for generating predictions.

    Handles the complete prediction workflow:
    - Model loading
    - Data loading
    - Prediction generation
    - Optional TTA
    - Results saving
    """

    def __init__(
        self,
        config: Any,
        model_path: str,
        model_type: str = "vision",
        use_tta: bool = False,
        **kwargs,
    ):
        """
        Initialize prediction pipeline.

        Args:
            config: Configuration object (VisionConfig or TabularConfig).
            model_path: Path to trained model checkpoint.
            model_type: Type of model ('vision' or 'tabular').
            use_tta: Whether to use test-time augmentation (vision only).
            **kwargs: Additional prediction parameters (test_data, image_dir, image_col, X_test, threshold).
        """
        super().__init__(config)
        self.kwargs = kwargs
        self.model_path = Path(model_path)
        self.model_type = model_type
        self.use_tta = use_tta
        self.model = None
        self.predictions = None

    def setup(self) -> None:
        """Setup prediction pipeline."""
        logger.info("🔧 Setting up prediction pipeline...")

        validate_config_section_exists(self.config, "paths")

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model path does not exist: {self.model_path}")

        if hasattr(self.config.paths, "output_dir"):
            output_dir = Path(self.config.paths.output_dir)
            ensure_dir(output_dir)
            ensure_dir(output_dir / "predictions")

        logger.info("✅ Prediction pipeline setup complete")

    def execute(self) -> Dict[str, Any]:
        """
        Execute prediction pipeline.

        Returns:
            Dictionary with prediction results:
            - 'success': bool
            - 'predictions': np.ndarray (predictions array)
            - 'output_path': str (path to saved predictions)
        """
        logger.info("🔮 Generating predictions...")

        if self.model_type == "vision":
            return self._predict_vision()
        elif self.model_type == "tabular":
            return self._predict_tabular()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def _predict_vision(self) -> Dict[str, Any]:
        """Generate predictions with vision model."""
        device = get_device(self.config.device if hasattr(self.config, "device") else "auto")

        logger.info(f"Loading model from {self.model_path}")
        checkpoint = torch.load(self.model_path, map_location=device)

        self.model = create_vision_model(
            model_name=self.config.model.name,
            num_classes=self.config.model.num_classes,
            pretrained=False,
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(device)
        self.model.eval()

        image_size = self.config.data.image_size if hasattr(self.config.data, "image_size") else 224
        batch_size = self.config.training.batch_size if hasattr(self.config, "training") else 32

        test_loader = create_test_dataloader(
            test_data=self.kwargs.get("test_data"),
            image_dir=self.kwargs.get("image_dir"),
            image_col=self.kwargs.get("image_col", "image_id"),
            image_size=image_size,
            batch_size=batch_size,
        )

        if self.use_tta:
            logger.info("Using Test-Time Augmentation")
            predictor = TTAPredictor(
                model=self.model,
                device=device,
                image_size=image_size,
            )
        else:
            predictor = VisionPredictor(model=self.model, device=device)

        self.predictions = predictor.predict(test_loader)

        output_path = Path(self.config.paths.output_dir) / "predictions" / "predictions.npy"
        ensure_dir(output_path.parent)
        np.save(output_path, self.predictions)

        logger.info(f"✅ Predictions complete. Saved to {output_path}")
        logger.info(f"  Shape: {self.predictions.shape}")

        return {
            "success": True,
            "predictions": self.predictions,
            "output_path": str(output_path),
        }

    def _predict_tabular(self) -> Dict[str, Any]:
        """Generate predictions with tabular model."""
        X_test = self.kwargs.get("X_test")
        if X_test is None:
            raise ValueError("X_test is required for tabular prediction")

        logger.info(f"Loading model from {self.model_path}")
        self.model = load_pickle(self.model_path)

        threshold = self.kwargs.get("threshold", 0.5)
        self.predictions = self.model.predict(X_test, threshold=threshold)

        output_path = Path(self.config.paths.output_dir) / "predictions" / "predictions.npy"
        ensure_dir(output_path.parent)
        np.save(output_path, self.predictions)

        logger.info(f"✅ Predictions complete. Saved to {output_path}")
        logger.info(f"  Shape: {self.predictions.shape}")

        return {
            "success": True,
            "predictions": self.predictions,
            "output_path": str(output_path),
        }

    def cleanup(self) -> None:
        """Cleanup prediction resources."""
        if self.model is not None and hasattr(self.model, "cpu"):
            self.model.cpu()

        self.model = None
