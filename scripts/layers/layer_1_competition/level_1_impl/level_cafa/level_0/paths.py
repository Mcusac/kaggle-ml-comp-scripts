"""CAFA 6 protein function prediction path constants."""

from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


class CAFAPaths(ContestPaths):
    """
    CAFA 6 protein function prediction path constants.
    
    Defines Kaggle dataset names and local paths for CAFA competition.
    """
    
    @property
    def kaggle_dataset_name(self) -> str:
        """CAFA main Kaggle dataset name."""
        return 'cafa-6-protein-function-prediction'
    
    @property
    def kaggle_competition_name(self) -> Optional[str]:
        """CAFA Kaggle competition name."""
        return 'cafa-6-protein-function-prediction'
    
    @property
    def local_data_path(self) -> str:
        """CAFA local data path."""
        return '../cafa-6-protein-function-prediction'
    
    # Additional CAFA-specific paths
    @property
    def kaggle_embeddings_dataset_name(self) -> str:
        """CAFA embeddings dataset name."""
        return 'cafa-6-embeddings'
    
    @property
    def kaggle_models_dataset_name(self) -> str:
        """CAFA models dataset name."""
        return 'cafa6-models'
    
    @property
    def kaggle_annotations_dataset_name(self) -> str:
        """CAFA GO annotations dataset name."""
        return 'protein-go-annotations'
