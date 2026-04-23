"""Memory cleanup utilities."""

import gc

from layers.layer_0_core.level_0 import get_logger, get_torch

_logger = get_logger(__name__)
_torch = get_torch()


def cleanup_gpu_memory() -> None:
    """
    Clean up GPU memory after training or inference.
    
    Essential for sequential training of multiple models on limited GPU memory.
    Also cleans up any pre-loaded data tensors.
    
    Lessons learned from Kaggle ML Competition:
    - Centralized GPU cleanup logic eliminates duplication
    - Should be called after each model training/inference
    - Clears CUDA cache and synchronizes before garbage collection
    """
    if _torch is None or not _torch.cuda.is_available():
        gc.collect()
        return

    try:
        _torch.cuda.empty_cache()
        _torch.cuda.synchronize()
        gc.collect()
        _torch.cuda.empty_cache()
    except Exception:
        gc.collect()

        
def perform_aggressive_cleanup() -> None:
    """
    Perform aggressive GPU memory cleanup.
    
    Includes resetting memory statistics and multiple cleanup passes
    for thorough memory release, useful for OOM recovery.
    """
    if _torch is None or not _torch.cuda.is_available():
        return
    
    try:
        # Reset peak memory statistics to help allocator release memory
        _torch.cuda.reset_peak_memory_stats()
    except RuntimeError as e:
        # CUDA memory stats operations may fail if device is unavailable or in invalid state
        raise RuntimeError("Could not reset peak memory stats:") from e
    
    # Additional aggressive cleanup passes (more passes for OOM recovery)
    for _ in range(5):
        gc.collect()
        if _torch is not None:
            try:
                _torch.cuda.empty_cache()
                _torch.cuda.synchronize()
            except RuntimeError:
                # CUDA operations may fail if device is unavailable or in invalid state
                pass
    
    # Try to collect any remaining CUDA tensors
    if _torch is not None:
        try:
            # Force collection of any remaining CUDA objects
            gc.collect()
            _torch.cuda.empty_cache()
        except RuntimeError:
            # CUDA operations may fail if device is unavailable or in invalid state
            pass
