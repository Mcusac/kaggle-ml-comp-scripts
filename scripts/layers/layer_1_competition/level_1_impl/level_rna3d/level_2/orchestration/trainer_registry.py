"""Maps RNA3D model names to trainer callables."""

import pickle
import pandas as pd

from pathlib import Path
from typing import Callable, Dict, Optional

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_rna3d.level_1 import build_templates, group_labels_to_coords

logger = get_logger(__name__)


def _train_baseline_approx(data_root: str, output_dir: str) -> None:
    """Train baseline_approx: build and cache template banks."""

    root = Path(data_root)
    train_sequences_path = root / "train_sequences.csv"
    train_labels_path = root / "train_labels.csv"

    if not train_sequences_path.exists() or not train_labels_path.exists():
        raise FileNotFoundError(f"Missing required files in {data_root}")

    train_seqs = pd.read_csv(train_sequences_path, usecols=["target_id", "sequence"])
    train_labels = pd.read_csv(train_labels_path)

    coords_by_target = group_labels_to_coords(train_labels)
    built = build_templates(train_seqs, coords_by_target)
    templates = [(t.target_id, t.sequence, t.coords) for t in built]

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    artifact_path = out_path / "baseline_approx_template_bank.pkl"

    with artifact_path.open("wb") as f:
        pickle.dump(
            {
                "templates": templates,
                "train_seqs": train_seqs.to_dict("records"),
            },
            f,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    logger.info(f"Saved baseline_approx template bank: {artifact_path}")
    logger.info(f"  Templates: {len(templates)}")


_MODEL_TRAINERS: Dict[str, Callable[[str, str], None]] = {
    "baseline_approx": _train_baseline_approx,
}


def get_trainer(model_name: str) -> Optional[Callable[[str, str], None]]:
    """Return the trainer callable for ``model_name``, or ``None`` if unknown."""
    return _MODEL_TRAINERS.get(model_name)


def list_available_models() -> list[str]:
    """Return registered model names in sorted order."""
    return sorted(_MODEL_TRAINERS.keys())
