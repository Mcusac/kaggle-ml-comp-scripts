"""Batch loading utilities. Uses level_0 for logging."""

from pathlib import Path
from typing import Callable, Iterable, List, Protocol, TypeVar, Union
from tqdm import tqdm

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)
T = TypeVar("T")


class BatchLoader(Protocol[T]):
    """
    Protocol for batch loaders: callable that loads multiple items from paths.
    Implementations can wrap load_batch with a specific loader (e.g. load_csv_batch).
    """

    def __call__(
        self,
        paths: Iterable[Union[str, Path]],
        *,
        desc: str = "Loading",
        show_progress: bool = False,
        **kwargs: object,
    ) -> List[T]:
        ...


def load_batch(
    paths: Iterable[Union[str, Path]],
    loader: Callable[[Union[str, Path]], T],
    *,
    desc: str = "Loading",
    show_progress: bool = False,
    item_name: str = "items",
    raise_on_error: bool = True,
) -> List[T]:
    """
    Load multiple items by applying a loader to each path.

    Args:
        paths: Iterable of file paths.
        loader: Callable that takes a path and returns a loaded item.
        desc: Progress bar description when show_progress is True.
        show_progress: If True, wrap iteration with tqdm when available.
        item_name: Used in log message, e.g. "CSV files", "images".
        raise_on_error: If True, raise on first load failure. If False, log and skip.

    Returns:
        List of loaded items in path order (skipped items omitted when raise_on_error=False).
    """
    paths_list = list(paths)
    if not paths_list:
        return []

    iterator = paths_list
    if show_progress:
        try:
            iterator = tqdm(paths_list, desc=desc)
        except ImportError:
            logger.debug("tqdm not available; progress disabled")

    results: List[T] = []
    for path in iterator:
        try:
            results.append(loader(path))
        except Exception as e:
            if raise_on_error:
                raise
            logger.warning("Skipping %s: %s", path, e)

    logger.info("Loaded %s %s", len(results), item_name)
    return results
