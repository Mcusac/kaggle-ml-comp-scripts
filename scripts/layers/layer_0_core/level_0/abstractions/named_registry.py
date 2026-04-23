"""A small, typed registry for name -> implementation mappings."""

from dataclasses import dataclass, field
from typing import Callable, Dict, Generic, Iterable, Optional, Sequence, TypeVar

_T = TypeVar("_T")


def build_unknown_key_error(*, registry_name: str, key_label: str, key: str, available: Sequence[str]) -> str:
    avail = ", ".join(available)
    return f"{key_label} {key!r} not found in {registry_name}. Available: [{avail}]"


@dataclass
class NamedRegistry(Generic[_T]):
    """
    A simple string-keyed registry with optional decorator-based registration.
    """

    registry_name: str
    key_label: str = "Key"
    _items: Dict[str, _T] = field(default_factory=dict)

    def register(self, key: str) -> Callable[[_T], _T]:
        k = str(key)

        def _decorator(obj: _T) -> _T:
            self._items[k] = obj
            return obj

        return _decorator

    def set(self, key: str, obj: _T) -> None:
        self._items[str(key)] = obj

    def get(self, key: str) -> Optional[_T]:
        return self._items.get(str(key))

    def require(self, key: str) -> _T:
        k = str(key)
        obj = self._items.get(k)
        if obj is None:
            raise ValueError(
                build_unknown_key_error(
                    registry_name=self.registry_name,
                    key_label=self.key_label,
                    key=k,
                    available=self.list_keys(),
                )
            )
        return obj

    def list_keys(self) -> list[str]:
        return sorted(self._items.keys())

    def contains(self, key: str) -> bool:
        return str(key) in self._items

    def bulk_validate_known(self, keys: Iterable[str]) -> None:
        available = self.list_keys()
        available_set = set(available)
        for k in keys:
            kk = str(k)
            if kk not in available_set:
                raise ValueError(
                    build_unknown_key_error(
                        registry_name=self.registry_name,
                        key_label=self.key_label,
                        key=kk,
                        available=available,
                    )
                )
