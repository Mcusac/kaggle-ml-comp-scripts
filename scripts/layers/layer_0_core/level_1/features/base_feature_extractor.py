"""Base for feature extractors: shared device handling and optional progress wrapping."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, TypeVar
from tqdm.auto import tqdm

from layers.layer_0_core.level_0 import get_logger, get_torch

_torch = get_torch()
_logger = get_logger(__name__)
_T = TypeVar("_T")


class BaseFeatureExtractor(ABC):
    """
    Base for feature extractors: shared device handling and optional progress wrapping.
    Subclasses must implement extract_features(); base provides common infrastructure.
    """

    def __init__(self, device: Optional[_torch.device] = None) -> None:
        if _torch is not None:
            self.device = device if device is not None else _torch.device(
                "cuda" if _torch.cuda.is_available() else "cpu"
            )
        else:
            self.device = device

    @abstractmethod
    def extract_features(self, *args: Any, **kwargs: Any) -> Any:
        """
        Extract features from input. Signature and return type are implementation-defined.
        Subclasses must implement this for a consistent public interface.
        """
        ...

    def _wrap_with_progress(
        self,
        iterable: Iterable[_T],
        desc: str,
        show_progress: bool,
    ) -> Iterable[_T]:
        """Wrap iterable with tqdm if show_progress and tqdm is available."""
        if not show_progress:
            return iterable
        try:
            return tqdm(iterable, desc=desc)
        except ImportError:
            _logger.debug("tqdm not available; progress disabled")
            return iterable
