"""Memory and resource cleanup utilities."""

import gc
import time

from typing import Any

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import is_cuda_available, perform_aggressive_cleanup

logger = get_logger(__name__)


def _safe_cuda_synchronize(torch) -> None:
    """Synchronize CUDA stream, suppressing RuntimeError if CUDA is unavailable."""
    try:
        torch.cuda.synchronize()
    except RuntimeError:
        pass


def cleanup_model(model: Any) -> None:
    """
    Release model resources by moving to CPU and clearing reference.

    Best-effort operation — logs failures but does not raise exceptions.
    Intended for use in finally blocks and error recovery paths.

    Args:
        model: Model object to clean up (may be None).
    """
    if model is None:
        return
    if not is_cuda_available():
        return

    torch = get_torch()
    if torch is None:
        return

    try:
        if isinstance(model, torch.nn.DataParallel):
            model.module.cpu()
        elif hasattr(model, 'cpu'):
            model.cpu()
    except Exception as e:
        logger.debug("Could not move model to CPU: %s", e)

    try:
        del model
    except Exception as e:
        logger.debug("Could not delete model reference: %s", e)


def release_training_resources(
    dataframe: Any = None,
    dataset: Any = None,
    dataloader: Any = None,
    model: Any = None,
    aggressive: bool = True,
    delay_seconds: float = 0.5,
) -> None:
    """
    Release memory held by training objects.

    Cleans up dataframes, datasets, dataloaders, and models, then flushes
    CUDA cache. When a dataframe was present, runs an additional round of
    CUDA cache flushes because dataframe memory is typically large and
    benefits from the extra pressure to release fragmented allocations.

    Args:
        dataframe: Optional dataframe to clean up.
        dataset: Optional dataset to clean up.
        dataloader: Optional dataloader to clean up.
        model: Optional model to clean up.
        aggressive: Whether to perform aggressive CUDA cleanup.
        delay_seconds: Delay in seconds between cleanup passes.
    """
    had_dataframe = _cleanup_dataframe(dataframe)
    cleanup_model(model)
    _cleanup_dataloader(dataloader)
    _cleanup_dataset(dataset)
    _cleanup_cuda(aggressive, delay_seconds)

    # Extra passes when a dataframe was present: large allocations leave more
    # fragmentation that a single flush may not fully reclaim.
    if had_dataframe:
        torch = get_torch()
        for _ in range(3):
            gc.collect()
            if torch is not None and is_cuda_available():
                try:
                    torch.cuda.empty_cache()
                except RuntimeError:
                    pass


def _cleanup_dataframe(dataframe: Any) -> bool:
    """
    Delete a dataframe and return True if one was present.

    The return value is used by release_training_resources to decide whether
    to run additional CUDA cleanup passes.
    """
    if dataframe is None:
        return False
    try:
        del dataframe
        return True
    except (AttributeError, RuntimeError) as e:
        logger.debug("Error deleting dataframe during cleanup: %s", e)
        return True
    except Exception as e:
        logger.debug("Unexpected error deleting dataframe during cleanup: %s", e, exc_info=True)
        return True


def _cleanup_dataset(dataset: Any) -> None:
    """Clear cached dataset attributes and delete the dataset object."""
    if dataset is None:
        return
    try:
        if hasattr(dataset, 'data_rows'):
            del dataset.data_rows
        if hasattr(dataset, 'data'):
            del dataset.data
        del dataset
    except (AttributeError, RuntimeError) as e:
        logger.debug("Error deleting dataset during cleanup: %s", e)
    except Exception as e:
        logger.debug("Unexpected error deleting dataset during cleanup: %s", e, exc_info=True)


def _cleanup_dataloader(dataloader: Any) -> None:
    """
    Shut down dataloader worker processes and delete the dataloader.

    Accesses dataloader._iterator which is a private PyTorch attribute.
    This may break across PyTorch versions — treat as best-effort.
    """
    if dataloader is None:
        return
    try:
        if hasattr(dataloader, '_iterator'):
            # NOTE: _iterator is a private PyTorch attribute; fragile across versions.
            try:
                iterator = dataloader._iterator
                if hasattr(iterator, '_shutdown'):
                    iterator._shutdown()
            except (AttributeError, RuntimeError) as e:
                logger.debug("Error closing dataloader iterator: %s", e)
            except Exception as e:
                logger.debug("Unexpected error closing dataloader iterator: %s", e, exc_info=True)
        del dataloader
    except (AttributeError, RuntimeError) as e:
        logger.debug("Error deleting dataloader during cleanup: %s", e)
    except Exception as e:
        logger.debug("Unexpected error deleting dataloader during cleanup: %s", e, exc_info=True)


def _cleanup_cuda(aggressive: bool, delay_seconds: float) -> None:
    """Flush CUDA memory with optional aggressive cleanup and delay."""
    if not is_cuda_available():
        gc.collect()
        return

    torch = get_torch()
    if torch is None:
        gc.collect()
        return

    _safe_cuda_synchronize(torch)

    try:
        torch.cuda.empty_cache()
    except RuntimeError:
        pass

    for _ in range(2):
        gc.collect()
        try:
            torch.cuda.empty_cache()
        except RuntimeError:
            pass

    _safe_cuda_synchronize(torch)

    if aggressive:
        perform_aggressive_cleanup()
        if delay_seconds > 0:
            time.sleep(delay_seconds)
            try:
                torch.cuda.empty_cache()
            except RuntimeError:
                pass
            _safe_cuda_synchronize(torch)
    else:
        try:
            torch.cuda.empty_cache()
        except RuntimeError:
            pass
        gc.collect()
        if delay_seconds > 0:
            time.sleep(delay_seconds)
            try:
                torch.cuda.empty_cache()
            except RuntimeError:
                pass