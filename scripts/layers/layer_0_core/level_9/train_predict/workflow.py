"""Train then predict workflow."""

from typing import Any, Dict

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import BasePipeline
from layers.layer_0_core.level_6 import PredictPipeline
from layers.layer_0_core.level_8 import TrainPipeline

_logger = get_logger(__name__)


class TrainPredictWorkflow(BasePipeline):
    """
    Workflow that trains a model and then generates predictions.

    Composes:
    - TrainPipeline: Train the model
    - PredictPipeline: Generate predictions on test data
    """

    def __init__(
        self,
        config: Any,
        model_type: str = 'vision',
        use_tta: bool = False,
        **kwargs
    ):
        """
        Initialize train-predict workflow.

        Args:
            config: Configuration object.
            model_type: Type of model ('vision' or 'tabular').
            use_tta: Whether to use test-time augmentation (vision only).
            **kwargs: Additional parameters passed to train and predict pipelines.
        """
        super().__init__(config)
        self.model_type = model_type
        self.use_tta = use_tta
        self.kwargs = kwargs
        self.train_results = None
        self.predict_results = None

    def setup(self) -> None:
        """Setup workflow."""
        _logger.info("🔧 Setting up train-predict workflow...")

        # Validate required data
        if self.model_type == 'vision':
            if 'train_data' not in self.kwargs or 'val_data' not in self.kwargs:
                raise ValueError("train_data and val_data required for vision training")
            if 'test_data' not in self.kwargs:
                raise ValueError("test_data required for prediction")
        elif self.model_type == 'tabular':
            if 'X_train' not in self.kwargs or 'y_train' not in self.kwargs:
                raise ValueError("X_train and y_train required for tabular training")
            if 'X_test' not in self.kwargs:
                raise ValueError("X_test required for prediction")

        _logger.info("✅ Train-predict workflow setup complete")

    def execute(self) -> Dict[str, Any]:
        """
        Execute train-predict workflow.

        Returns:
            Dictionary with combined results from training and prediction.
        """
        _logger.info("🚀 Starting train-predict workflow...")

        # Step 1: Train
        _logger.info("=" * 60)
        _logger.info("STEP 1: Training Model")
        _logger.info("=" * 60)

        train_pipeline = TrainPipeline(
            config=self.config,
            model_type=self.model_type,
            **self.kwargs
        )

        self.train_results = train_pipeline.run()

        if not self.train_results['success']:
            raise RuntimeError("Training failed")

        # Step 2: Predict
        _logger.info("=" * 60)
        _logger.info("STEP 2: Generating Predictions")
        _logger.info("=" * 60)

        predict_pipeline = PredictPipeline(
            config=self.config,
            model_path=self.train_results['model_path'],
            model_type=self.model_type,
            use_tta=self.use_tta,
            **self.kwargs
        )

        self.predict_results = predict_pipeline.run()

        if not self.predict_results['success']:
            raise RuntimeError("Prediction failed")

        _logger.info("✅ Train-predict workflow complete")

        return {
            'success': True,
            'training': self.train_results,
            'prediction': self.predict_results,
            'predictions_path': self.predict_results['output_path']
        }

    def cleanup(self) -> None:
        """Cleanup workflow resources."""
        # Nothing specific to clean up
        pass
