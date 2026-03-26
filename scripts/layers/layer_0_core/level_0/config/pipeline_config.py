"""Pipeline configuration settings."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""

    grid_search_n_jobs: int = -1
    grid_search_verbose: int = 1
    grid_search_pre_dispatch: str = '2*n_jobs'
    cv_n_folds: int = 5
    cv_shuffle: bool = True
    cv_random_state: int = 42
    ensemble_method: str = 'weighted_average'
    ensemble_n_models: int = 3
    ensemble_weights: Optional[List[float]] = None
    export_format: str = 'pytorch'
    export_include_metadata: bool = True
    checkpoint_dir: str = 'checkpoints'
    results_dir: str = 'results'
    logs_dir: str = 'logs'

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'grid_search': {
                'n_jobs': self.grid_search_n_jobs,
                'verbose': self.grid_search_verbose,
                'pre_dispatch': self.grid_search_pre_dispatch
            },
            'cross_validation': {
                'n_folds': self.cv_n_folds,
                'shuffle': self.cv_shuffle,
                'random_state': self.cv_random_state
            },
            'ensembling': {
                'method': self.ensemble_method,
                'n_models': self.ensemble_n_models,
                'weights': self.ensemble_weights
            },
            'export': {
                'format': self.export_format,
                'include_metadata': self.export_include_metadata
            },
            'directories': {
                'checkpoint_dir': self.checkpoint_dir,
                'results_dir': self.results_dir,
                'logs_dir': self.logs_dir
            }
        }
