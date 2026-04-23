"""Base pipeline abstract class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


class BasePipeline(ABC):
    """
    Abstract base class for all pipelines.

    Pipelines are high-level orchestration units that combine multiple
    operations (data loading, training, prediction, evaluation) into
    complete workflows.

    All pipelines follow a common lifecycle:
    1. setup() - Initialize and validate
    2. execute() - Run the pipeline
    3. cleanup() - Clean up resources
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize pipeline.

        Args:
            config: Configuration object (domain-specific config).
        """
        self.config = config
        self.results: Optional[Dict[str, Any]] = None

    @abstractmethod
    def setup(self) -> None:
        """
        Setup pipeline: validate inputs, create directories, initialize components.

        This method should:
        - Validate configuration
        - Create output directories
        - Initialize required components
        - Check prerequisites

        Raises:
            ValueError: If configuration is invalid.
            FileNotFoundError: If required files don't exist.
        """
        ...

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Execute the pipeline.

        This is the main pipeline logic. Should return a dictionary
        with results (metrics, paths, etc.).

        Returns:
            Dictionary with pipeline results. Should include:
            - 'success': bool
            - 'metrics': dict (optional)
            - 'output_paths': dict (optional)
            - 'metadata': dict (optional)

        Raises:
            RuntimeError: If pipeline execution fails.
        """
        ...

    def cleanup(self) -> None:
        """
        Cleanup pipeline resources.

        This method is called after execute() to clean up any resources
        (close files, release memory, etc.). Override if needed.
        """
        pass

    def run(self) -> Dict[str, Any]:
        """
        Run the complete pipeline lifecycle.

        Returns:
            Pipeline results dictionary.
        """
        try:
            _logger.info("🚀 Starting pipeline: %s", self.__class__.__name__)
            self.setup()
            self.results = self.execute()
            self.cleanup()
            _logger.info("✅ Pipeline completed: %s", self.__class__.__name__)
            return self.results
        except Exception as e:
            _logger.error("❌ Pipeline failed: %s", self.__class__.__name__)
            _logger.error("  Error: %s", str(e))
            raise
