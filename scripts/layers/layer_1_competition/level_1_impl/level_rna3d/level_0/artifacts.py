"""RNA3D prediction artifact helpers.

Defines a simple, explicit on-disk format for predictions used by
training/tuning/ensemble/stacking pipelines.

The core structure is:
    preds[target_id] -> np.ndarray[L, n_structures, 3]
plus lightweight metadata.
"""

import numpy as np

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from layers.layer_0_core.level_4 import PICKLE_HIGHEST_PROTOCOL, load_pickle, save_pickle


ARTIFACT_VERSION = "rna3d_pred_v1"


@dataclass
class PredictionArtifact:
    """Container for RNA3D predictions and minimal metadata."""

    predictions: Dict[str, np.ndarray]
    n_structures: int
    metadata: Dict[str, object]
    version: str = ARTIFACT_VERSION

    def validate(self) -> None:
        """Basic sanity checks on the artifact structure."""
        for tid, arr in self.predictions.items():
            if arr.ndim != 3 or arr.shape[2] != 3:
                raise ValueError(
                    f"Prediction for {tid!r} must have shape (L, K, 3), got {arr.shape}"
                )
            if arr.shape[1] != self.n_structures:
                raise ValueError(
                    f"Prediction for {tid!r} has {arr.shape[1]} structures, "
                    f"expected {self.n_structures}"
                )


def save_prediction_artifact(artifact: PredictionArtifact, path: str | Path) -> None:
    """Serialize a PredictionArtifact to disk (pickle).

    Args:
        artifact: PredictionArtifact instance (validated before save).
        path: Target path.
    """
    artifact.validate()
    out_path = Path(path)
    save_pickle(
        {
            "version": artifact.version,
            "n_structures": artifact.n_structures,
            "metadata": artifact.metadata,
            "predictions": artifact.predictions,
        },
        out_path,
        protocol=PICKLE_HIGHEST_PROTOCOL,
    )


def load_prediction_artifact(path: str | Path) -> PredictionArtifact:
    """Load a PredictionArtifact from disk."""
    in_path = Path(path)
    obj = load_pickle(in_path)

    version = obj.get("version", ARTIFACT_VERSION)
    if version != ARTIFACT_VERSION:
        # For now we only support a single version; fail fast if mismatch.
        raise ValueError(f"Unsupported prediction artifact version: {version}")

    preds = obj["predictions"]
    n_structures = int(obj["n_structures"])
    metadata = obj.get("metadata", {}) or {}

    # Ensure arrays are np.ndarray with float32 dtype
    for tid, arr in list(preds.items()):
        preds[tid] = np.asarray(arr, dtype=np.float32)

    artifact = PredictionArtifact(
        predictions=preds,
        n_structures=n_structures,
        metadata=metadata,
        version=version,
    )
    artifact.validate()
    return artifact
