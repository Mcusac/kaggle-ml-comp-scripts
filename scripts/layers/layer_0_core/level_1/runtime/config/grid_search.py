"""Shared configuration for grid search modes."""

from dataclasses import dataclass

from level_0 import RuntimeConfig


@dataclass
class GridSearchConfig(RuntimeConfig): 
    """Grid search configuration and settings."""
    
    # Result management
    keep_top_variants: int = 20
    cleanup_interval: int = 10
    enable_cleanup: bool = True
    delete_checkpoints_after_completion: bool = True
    
    # Dataset caching
    use_streaming_dataset: bool = True
    
    # OOM (Out of Memory) handling
    min_batch_size: int = 4
    batch_size_reduction_factor: int = 2
    max_oom_retries: int = 2
    
    # Parallel execution
    n_jobs: int = 1  # Number of parallel jobs (1 = sequential)
    
    # Checkpoint management
    enable_checkpointing: bool = True
    checkpoint_interval: int = 1  # Save checkpoint every N variants
    
    # Progress tracking
    show_progress: bool = True
    log_interval: int = 1  # Log every N variants
