"""
Memory management utilities - pure runtime facts.

Returns GPU memory statistics without logging side effects.
Callers can log as needed at their layer.
"""

import psutil
import numpy as np

from typing import Optional

from layers.layer_0_core.level_0 import get_torch, is_torch_available


def get_model_memory_usage() -> Optional[float]:
    """
    Get approximate GPU memory usage in MB.
    
    Returns:
        Memory usage in MB, or None if CUDA unavailable
        
    Example:
        >>> mem = get_model_memory_usage()
        >>> if mem and mem > 1000:
        ...     print("High memory usage detected")
    """
    torch = get_torch()

    if not is_torch_available() or not torch.cuda.is_available():
        return None
    
    try:
        return torch.cuda.memory_allocated() / (1024 ** 2)
    except Exception:
        return None


def estimate_memory_mb(array: np.ndarray) -> float:
    """
    Estimate memory usage of a numpy array in MB.
    
    Args:
        array: Numpy array
        
    Returns:
        Estimated memory in megabytes
        
    Example:
        >>> arr = np.zeros((1000, 1000))
        >>> mem = estimate_memory_mb(arr)
        >>> print(f"Array uses {mem:.2f} MB")
    """
    return array.nbytes / (1024 ** 2)


def get_available_memory_mb() -> float:
    """
    Get available system memory in MB.
    
    Returns:
        Available memory in megabytes
        
    Example:
        >>> free_mem = get_available_memory_mb()
        >>> if free_mem < 1000:
        ...     print("Low memory warning!")
    """
    return psutil.virtual_memory().available / (1024 ** 2)


def get_total_memory_mb() -> float:
    """
    Get total system memory in MB.
    
    Returns:
        Total memory in megabytes
    """
    return psutil.virtual_memory().total / (1024 ** 2)


def get_memory_usage_percent() -> float:
    """
    Get current memory usage as percentage.
    
    Returns:
        Memory usage percentage (0-100)
    """
    return psutil.virtual_memory().percent