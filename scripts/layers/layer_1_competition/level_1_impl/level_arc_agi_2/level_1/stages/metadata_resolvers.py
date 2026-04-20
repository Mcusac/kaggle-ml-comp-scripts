"""Metadata / JSON resolution helpers for the ARC stages.

Groups all train-metadata readers used by train / tune / submit:
- ``_default_chosen_params`` (default chosen-params for registered neural models)
- ``_resolve_chosen_params_for_submit`` (tuned-config or train-metadata fallback)
- ``_get_per_model_entry`` (per-model sub-object lookup)
- ``_resolve_neural_paths_from_entry`` (checkpoint + train-config paths)

All pre-existing ``except Exception`` + ``logger.warning`` blocks are preserved
verbatim (metadata-read failures must never abort a pipeline).
"""

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_json_raw

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    DEFAULT_SUBMIT_HEURISTIC,
    load_chosen_params_from_tuned_config,
)

logger = get_logger(__name__)


def default_chosen_params() -> dict[str, Any]:
    return {"heuristic": DEFAULT_SUBMIT_HEURISTIC, "version": 1}


def resolve_chosen_params_for_submit(
    tuned_config_path: Optional[str],
    train_metadata_json: Optional[str],
    primary_model: str,
) -> dict[str, Any] | None:
    if tuned_config_path and str(tuned_config_path).strip():
        cp = load_chosen_params_from_tuned_config(str(tuned_config_path))
        if cp:
            return cp
    if train_metadata_json and str(train_metadata_json).strip():
        p = Path(str(train_metadata_json).strip())
        if p.is_file():
            try:
                data = load_json_raw(p)
                if isinstance(data, dict):
                    if isinstance(data.get("chosen_params"), dict):
                        return dict(data["chosen_params"])
                    pm = data.get("per_model")
                    if isinstance(pm, dict):
                        entry = pm.get(str(primary_model))
                        if isinstance(entry, dict) and isinstance(entry.get("chosen_params"), dict):
                            return dict(entry["chosen_params"])
                    models = data.get("models")
                    if isinstance(models, list) and models and isinstance(pm, dict):
                        first = str(models[0])
                        entry = pm.get(first)
                        if isinstance(entry, dict) and isinstance(entry.get("chosen_params"), dict):
                            return dict(entry["chosen_params"])
            except Exception as e:
                logger.warning("Could not read train metadata for submit chosen_params: %s", e)
    return None


def get_per_model_entry(train_metadata_json: Optional[str], model_name: str) -> dict[str, Any] | None:
    if not train_metadata_json or not str(train_metadata_json).strip():
        return None
    p = Path(str(train_metadata_json).strip())
    if not p.is_file():
        return None
    try:
        data = load_json_raw(p)
        if not isinstance(data, dict):
            return None
        pm = data.get("per_model")
        if isinstance(pm, dict):
            entry = pm.get(str(model_name))
            if isinstance(entry, dict):
                return entry
    except Exception as e:
        logger.warning("Could not read per_model from train metadata: %s", e)
    return None


def resolve_neural_paths_from_entry(entry: dict[str, Any] | None) -> tuple[Path | None, Path | None]:
    if not entry:
        return None, None
    art = entry.get("artifacts")
    if not isinstance(art, dict):
        return None, None
    ckpt = art.get("checkpoint")
    cfg = art.get("train_config")
    if not ckpt or not cfg:
        return None, None
    cp = Path(str(ckpt))
    tp = Path(str(cfg))
    if cp.is_file() and tp.is_file():
        return cp, tp
    return None, None
