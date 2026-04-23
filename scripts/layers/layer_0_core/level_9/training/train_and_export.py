"""Train and export workflow."""

from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import BasePipeline
from layers.layer_0_core.level_5 import ExportPipeline
from layers.layer_0_core.level_8 import TrainPipeline

_logger = get_logger(__name__)


class TrainAndExportWorkflow(BasePipeline):
    """
    Workflow that trains a model and exports it for submission.

    Composes:
    - TrainPipeline: Train the model
    - ExportPipeline: Export the trained model
    """

    def __init__(
        self,
        config: Any,
        model_type: str = 'vision',
        export_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize train-and-export workflow.

        Args:
            config: Configuration object.
            model_type: Type of model ('vision' or 'tabular').
            export_dir: Optional export directory (default: config.paths.output_dir / 'exports').
            **kwargs: Additional parameters passed to train and export pipelines.
        """
        super().__init__(config)
        self.kwargs = kwargs
        self.model_type = model_type
        self.export_dir = export_dir
        self.train_results = None
        self.export_results = None

    def setup(self) -> None:
        """Setup workflow."""
        _logger.info("🔧 Setting up train-and-export workflow...")

        # Validate required data
        if self.model_type == 'vision':
            if 'train_data' not in self.kwargs or 'val_data' not in self.kwargs:
                raise ValueError("train_data and val_data required for vision training")
        elif self.model_type == 'tabular':
            if 'X_train' not in self.kwargs or 'y_train' not in self.kwargs:
                raise ValueError("X_train and y_train required for tabular training")

        _logger.info("✅ Train-and-export workflow setup complete")

    def execute(self) -> Dict[str, Any]:
        """
        Execute train-and-export workflow.

        Returns:
            Dictionary with combined results from training and export.
        """
        _logger.info("🚀 Starting train-and-export workflow...")

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

        # Step 2: Export
        _logger.info("=" * 60)
        _logger.info("STEP 2: Exporting Model")
        _logger.info("=" * 60)

        export_pipeline = ExportPipeline(
            config=self.config,
            model_path=self.train_results['model_path'],
            export_dir=self.export_dir,
            model_type=self.model_type,
            additional_metadata={
                'training_metrics': self.train_results['metrics'],
                'training_history': self.train_results.get('history', [])
            }
        )

        self.export_results = export_pipeline.run()

        if not self.export_results['success']:
            raise RuntimeError("Export failed")

        _logger.info("✅ Train-and-export workflow complete")

        return {
            'success': True,
            'training': self.train_results,
            'export': self.export_results,
            'export_path': self.export_results['export_path'],
            'export_dir': self.export_results['export_dir']
        }

    def cleanup(self) -> None:
        """Cleanup workflow resources."""
        pass
