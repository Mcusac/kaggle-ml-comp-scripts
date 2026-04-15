"""Submission CSV persistence helpers."""

import pandas as pd

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import get_logger, is_kaggle
from layers.layer_0_core.level_1 import get_default_submission_csv_path
from layers.layer_0_core.level_4 import save_csv

logger = get_logger(__name__)


def save_submission_csv(
    submission_df: pd.DataFrame,
    output_path: Optional[str] = None,
) -> str:
    """
    Save submission CSV to the environment-default output location, optionally overridden.

    On Kaggle, also writes to the canonical working-dir submission path when different.
    """
    out = output_path or str(get_default_submission_csv_path(purpose="output"))
    save_csv(submission_df, out, index=False)

    if is_kaggle():
        kaggle_path = get_default_submission_csv_path(purpose="output")
        if Path(out).resolve() != kaggle_path.resolve():
            save_csv(submission_df, str(kaggle_path), index=False)
            logger.info(f"Also wrote {kaggle_path}")

    return str(out)

