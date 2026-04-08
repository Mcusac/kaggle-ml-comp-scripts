"""Model export pipeline."""

from typing import Dict, Any, Optional
from pathlib import Path
import shutil

from level_0 import ensure_dir, get_logger
from level_1 import BasePipeline, validate_config_section_exists
from level_4 import save_json

logger = get_logger(__name__)


class ExportPipeline(BasePipeline):
    """
    Atomic pipeline for exporting models.
    
    Handles the complete export workflow:
    - Load model checkpoint
    - Create export package (model + metadata)
    - Save to export directory
    """
    
    def __init__(
        self,
        config: Any,
        model_path: str,
        export_dir: Optional[str] = None,
        model_type: str = 'vision',  # 'vision' or 'tabular'
        **kwargs
    ):
        """
        Initialize export pipeline.
        
        Args:
            config: Configuration object (VisionConfig or TabularConfig).
            model_path: Path to trained model checkpoint.
            export_dir: Optional export directory (default: config.paths.output_dir / 'exports').
            model_type: Type of model ('vision' or 'tabular').
            **kwargs: Additional export parameters (metadata, etc.).
        """
        super().__init__(config, **kwargs)
        self.model_path = Path(model_path)
        self.export_dir = Path(export_dir) if export_dir else None
        self.model_type = model_type
    
    def setup(self) -> None:
        """Setup export pipeline."""
        logger.info("🔧 Setting up export pipeline...")
        
        # Validate config
        validate_config_section_exists(self.config, 'paths')
        
        # Validate model path
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model path does not exist: {self.model_path}")
        
        # Determine export directory
        if self.export_dir is None:
            self.export_dir = Path(self.config.paths.output_dir) / 'exports'
        
        ensure_dir(self.export_dir)
        
        logger.info("✅ Export pipeline setup complete")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute export pipeline.
        
        Returns:
            Dictionary with export results:
            - 'success': bool
            - 'export_path': str (path to exported model)
            - 'metadata_path': str (path to metadata file)
        """
        logger.info("📦 Exporting model...")
        
        # Create export subdirectory with model name
        model_name = self.model_path.stem
        export_subdir = self.export_dir / model_name
        ensure_dir(export_subdir)
        
        # Copy model file
        export_model_path = export_subdir / self.model_path.name
        shutil.copy2(self.model_path, export_model_path)
        logger.info(f"Copied model to {export_model_path}")
        
        # Create metadata
        metadata = {
            'model_path': str(export_model_path),
            'model_type': self.model_type,
            'config': self._extract_config_metadata(),
            **self.kwargs.get('additional_metadata', {})
        }
        
        # Save metadata
        metadata_path = export_subdir / 'metadata.json'
        save_json(metadata, metadata_path)
        logger.info(f"Saved metadata to {metadata_path}")
        
        logger.info(f"✅ Export complete. Model exported to {export_subdir}")
        
        return {
            'success': True,
            'export_path': str(export_model_path),
            'metadata_path': str(metadata_path),
            'export_dir': str(export_subdir)
        }
    
    def _extract_config_metadata(self) -> Dict[str, Any]:
        """Extract relevant metadata from config."""
        metadata = {}
        
        # Extract model info
        if hasattr(self.config, 'model'):
            metadata['model'] = {
                'name': getattr(self.config.model, 'name', None),
                'num_classes': getattr(self.config.model, 'num_classes', None),
                'pretrained': getattr(self.config.model, 'pretrained', None),
            }
        
        # Extract training info
        if hasattr(self.config, 'training'):
            metadata['training'] = {
                'num_epochs': getattr(self.config.training, 'num_epochs', None),
                'batch_size': getattr(self.config.training, 'batch_size', None),
                'learning_rate': getattr(self.config.training, 'learning_rate', None),
                'optimizer': getattr(self.config.training, 'optimizer', None),
            }
        
        # Extract data info
        if hasattr(self.config, 'data'):
            metadata['data'] = {
                'image_size': getattr(self.config.data, 'image_size', None),
                'augmentation': getattr(self.config.data, 'augmentation', None),
            }
        
        return metadata
    
    def cleanup(self) -> None:
        """Cleanup export resources."""
        # Nothing to clean up for export
        pass
