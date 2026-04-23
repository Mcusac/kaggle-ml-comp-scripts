"""RNA3D data validation utilities.

Kept intentionally lightweight: fast sanity checks that catch path/schema issues
before running longer pipelines.
"""
import pandas as pd

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def validate_rna3d_inputs(data_root: str, max_targets: int = 0) -> None:
    """
    Validate presence and basic schema of RNA3D CSV inputs.

    Args:
        data_root: Directory containing competition CSVs.
        max_targets: If >0, only validate first N test targets for deeper checks.
    """
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    train_sequences_path = root / "train_sequences.csv"
    test_sequences_path = root / "test_sequences.csv"
    train_labels_path = root / "train_labels.csv"

    for p in (train_sequences_path, test_sequences_path, train_labels_path):
        if not p.exists():
            raise FileNotFoundError(f"Missing required input file: {p}")

    train_seqs = pd.read_csv(train_sequences_path)
    test_seqs = pd.read_csv(test_sequences_path)
    train_labels = pd.read_csv(train_labels_path)

    _require_columns(train_seqs, {"target_id", "sequence"}, "train_sequences.csv")
    _require_columns(test_seqs, {"target_id", "sequence"}, "test_sequences.csv")
    _require_columns(train_labels, {"ID", "resname", "resid", "x_1", "y_1", "z_1"}, "train_labels.csv")

    if train_seqs["target_id"].isna().any() or train_seqs["sequence"].isna().any():
        raise ValueError("train_sequences.csv contains null target_id or sequence")
    if test_seqs["target_id"].isna().any() or test_seqs["sequence"].isna().any():
        raise ValueError("test_sequences.csv contains null target_id or sequence")

    if max_targets and max_targets > 0:
        test_subset = test_seqs.head(int(max_targets))
        if test_subset.empty:
            raise ValueError("test_sequences.csv is empty")

    # NOTE: Keep logs ASCII-safe for Windows consoles (cp1252).
    _logger.info("RNA3D inputs look OK")
    _logger.info("   train_sequences: %d rows", len(train_seqs))
    _logger.info("   test_sequences: %d rows", len(test_seqs))
    _logger.info("   train_labels: %d rows", len(train_labels))
