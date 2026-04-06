"""Source handlers that resolve model artifacts for export."""

from __future__ import annotations

import csv
import json

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_5 import find_trained_model_path

from layers.layer_1_competition.level_0_infra.level_1.export.metadata_builders import (
    build_end_to_end_metadata,
    build_regression_metadata,
)

logger = get_logger(__name__)


def handle_just_trained_model(
    model_dir: str,
    config: Any,
    variant_id: Optional[str] = None,
    variant_info: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """Handle export from a just-trained model directory."""
    model_dir_path = Path(model_dir)
    if not model_dir_path.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir_path}")
    model_path, best_fold = find_trained_model_path(model_dir_path)
    if model_path.suffix == ".pkl":
        metadata = build_regression_metadata(config, model_path, best_fold, variant_id, variant_info)
    else:
        metadata = build_end_to_end_metadata(config, model_path, best_fold, variant_id, variant_info)
    return model_path, metadata


def handle_best_variant_file(
    best_variant_file: str,
    config: Any,
    export_dir: Optional[str] = None,
    paths: Optional[Any] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """Read best variant pointer file, resolve model dir, then export."""
    path = Path(best_variant_file)
    if not path.exists():
        raise FileNotFoundError(f"Best variant file not found: {path}")
    with open(path, "r") as f:
        data = json.load(f)
    model_dir = data.get("model_dir")
    if not model_dir and data.get("variant_id") and paths:
        model_dir = str(paths.get_models_base_dir() / "dataset_grid_search" / data["variant_id"])
    if not model_dir:
        raise ValueError("Best variant file must contain 'model_dir' or 'variant_id' (with paths)")
    return handle_just_trained_model(model_dir=model_dir, config=config)


def handle_results_file(
    results_file: str,
    variant_id: str,
    config: Any,
    export_dir: Optional[str] = None,
    paths: Optional[Any] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """Read results file, resolve a variant model dir, then export."""
    path = Path(results_file)
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")
    if path.suffix.lower() == ".json":
        with open(path, "r") as f:
            raw = json.load(f)
        if isinstance(raw, list):
            results = raw
        elif isinstance(raw, dict) and "results" in raw:
            results = raw["results"]
        else:
            results = [raw] if isinstance(raw, dict) else []
    else:
        results = _parse_results_csv(path)
    variant = None
    for row in results:
        if isinstance(row, dict) and row.get("variant_id") == variant_id:
            variant = row
            break
    if not variant:
        raise ValueError(f"Variant {variant_id} not found in results file")
    model_dir = variant.get("model_dir") or variant.get("model_path")
    if not model_dir and paths:
        model_dir = str(paths.get_models_base_dir() / "dataset_grid_search" / variant_id)
    if not model_dir:
        raise ValueError(f"Cannot resolve model_dir for variant {variant_id}")
    return handle_just_trained_model(
        model_dir=model_dir,
        config=config,
        variant_id=variant_id,
        variant_info=variant if isinstance(variant, dict) else None,
    )


def handle_auto_detect(
    model_dir: str,
    config: Any,
    export_dir: Optional[str] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """Scan model_dir for best model and export."""
    return handle_just_trained_model(model_dir=model_dir, config=config)


def _parse_results_csv(path: Path) -> list:
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip() if isinstance(k, str) else k: v for k, v in row.items()})
    return rows

