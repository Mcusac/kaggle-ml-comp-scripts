"""Tuned-config IO: load chosen_params from a best_config.json produced by the tuning phase."""

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json_raw

logger = get_logger(__name__)


def load_chosen_params_from_tuned_config(path: str | None) -> dict[str, Any] | None:
    """Load chosen_params from best_config.json; return None on missing or invalid input."""
    if not path or not str(path).strip():
        return None
    p = Path(str(path).strip())
    if not p.is_file():
        logger.warning("Tuned config path missing or not a file: %s", p)
        return None
    try:
        data = load_json_raw(p)
        if not isinstance(data, dict):
            logger.warning("Tuned config is not a JSON object: %s", p)
            return None
        cp = data.get("chosen_params")
        if not isinstance(cp, dict):
            logger.warning("Tuned config has no chosen_params dict: %s", p)
            return None
        return dict(cp)
    except Exception as e:
        logger.warning("Failed to load tuned config %s: %s", p, e)
        return None