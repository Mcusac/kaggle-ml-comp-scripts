"""Lazy imports logic."""

from typing import Iterable, Union, Tuple, Any

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def lazy_import(
    module: str,
    attrs: Union[str, Iterable[str]],
    *,
    package: str,
    warn: str,
) -> Union[Any, Tuple[Any, ...], None]:
    """
    Generic lazy importer.
    """

    if isinstance(attrs, str):
        attrs = (attrs,)
        single = True
    else:
        single = False

    try:
        mod = __import__(module, fromlist=list(attrs))
        values = tuple(getattr(mod, a) for a in attrs)
        return values[0] if single else values

    except Exception:
        _logger.warning("%s not available. %s", package, warn)

        if single:
            return None

        return tuple(None for _ in attrs)