"""CSV IO helpers for contest data loading (infrastructure-level)."""

import pandas as pd

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_csv_raw

logger = get_logger(__name__)


def load_training_csv(
    *,
    contest_entry: dict,
    train_csv_path: Path,
) -> pd.DataFrame:
    loader_fn = (contest_entry or {}).get("training_data_loader")
    return loader_fn(train_csv_path) if loader_fn else load_csv_raw(train_csv_path)

