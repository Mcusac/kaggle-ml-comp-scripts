"""Generic JSON configuration loader. Uses level_0 and level_4.load_json."""

from pathlib import Path
from typing import Dict, Any, Optional, List

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json

_logger = get_logger(__name__)


class JSONConfigLoader:
    """
    Generic JSON configuration loader.
    """

    def __init__(
        self,
        config_name: str,
        config_dir: str = "config",
        lowercase_keys: bool = True,
    ):
        self.config_name = config_name
        self.config_dir = Path(config_dir)
        self.lowercase_keys = lowercase_keys

        self._data: Dict[str, Any] = {}

        self._load()

    def _load(self) -> None:
        path = self.config_dir / f"{self.config_name}.json"

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        _logger.info("Loading config: %s", path)

        data = load_json(path)

        if self.lowercase_keys:
            data = {k.lower(): v for k, v in data.items()}

        self._data = data

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key.lower())

    def keys(self) -> List[str]:
        return list(self._data.keys())

    def all(self) -> Dict[str, Any]:
        return self._data.copy()

    def reload(self) -> None:
        """Reload config from disk."""
        self._load()
