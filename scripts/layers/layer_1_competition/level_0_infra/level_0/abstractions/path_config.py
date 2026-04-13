"""Contest path configuration for data, models, and outputs."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ContestPathConfig:
    """Path configuration for contest runs (data, models, outputs, cache)."""

    # Data paths
    data_root: Optional[str] = None  # Will be set from contest if None
    train_csv: str = 'train.csv'
    test_csv: str = 'test.csv'

    # Output paths
    output_dir: str = 'output'
    model_dir: str = 'models'
    log_dir: str = 'logs'
    submission_dir: str = 'submissions'

    # Cache paths
    cache_dir: str = 'cache'
    feature_cache_dir: Optional[str] = None
    model_cache_dir: Optional[str] = None
