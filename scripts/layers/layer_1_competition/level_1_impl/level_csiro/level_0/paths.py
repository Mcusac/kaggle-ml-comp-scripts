"""CSIRO biomass competition path constants."""

import os

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import is_kaggle_input

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


class CSIROPaths(ContestPaths):
    """
    CSIRO biomass competition path constants.
    
    Defines Kaggle dataset names and local path defaults for the CSIRO competition.
    """
    
    @property
    def kaggle_dataset_name(self) -> str:
        """CSIRO main Kaggle input dataset name."""
        return 'csiro-biomass'
    
    @property
    def kaggle_competition_name(self) -> Optional[str]:
        """CSIRO Kaggle competition name."""
        return 'csiro-biomass'
    
    @property
    def local_data_path(self) -> str:
        """CSIRO default local data root path."""
        return '../csiro-biomass'
    
    # Additional CSIRO-specific dataset paths
    @property
    def kaggle_models_dataset_name(self) -> str:
        """CSIRO Kaggle models dataset name."""
        return 'csiro-models'
    
    @property
    def kaggle_metadata_dataset_name(self) -> str:
        """CSIRO Kaggle metadata dataset name."""
        return 'csiro-metadata'
    
    def get_models_base_dir(self) -> Path:
        """Base directory for uploaded regression models (csiro-models).
        On Kaggle: /kaggle/input/csiro-models; locally: CSIRO_MODELS_BASE_DIR or ../csiro-models.
        """
        if is_kaggle_input('/kaggle/input'):
            return Path(f'/kaggle/input/{self.kaggle_models_dataset_name}')
        return Path(os.environ.get('CSIRO_MODELS_BASE_DIR', '../csiro-models'))
    
    @property
    def kaggle_features_dataset_name(self) -> str:
        """CSIRO Kaggle features dataset name."""
        return 'csiro-extracted-features'
