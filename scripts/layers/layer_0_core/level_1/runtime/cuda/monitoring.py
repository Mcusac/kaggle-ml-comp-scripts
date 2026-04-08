"""Memory monitoring utilities."""

from level_0 import get_logger, get_torch

logger = get_logger(__name__)


def print_gpu_memory_status() -> None:
    """
    Log GPU memory status if available.
    
    Gracefully handles missing torch or CUDA. Only logs in Kaggle environment.
    """  
    try:
        torch = get_torch()
        if torch.cuda.is_available():
            BYTES_PER_GB = 1024 * 1024 * 1024
            allocated = torch.cuda.memory_allocated() / BYTES_PER_GB
            reserved = torch.cuda.memory_reserved() / BYTES_PER_GB
            logger.info(f"📊 GPU Memory Status (before grid search):")
            logger.info(f"   Allocated: {allocated:.2f} GB")
            logger.info(f"   Reserved: {reserved:.2f} GB")
    except ImportError:
        # torch not available - skip GPU memory check
        pass
    except (RuntimeError, AttributeError) as e:
        # CUDA errors or attribute access issues - log but don't fail
        raise RuntimeError("Could not check GPU memory status:") from e
    except Exception as e:
        # Catch any other unexpected errors - log but don't fail
        raise RuntimeError("Unexpected error checking GPU memory:") from e