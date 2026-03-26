"""Batch loading for CSV files. Uses level_1.load_batch and level_4.load_csv."""

from pathlib import Path
from typing import Iterable, List, Union

import pandas as pd

from layers.layer_0_core.level_1 import load_batch
from level_4 import load_csv


def load_csv_batch(
    paths: Iterable[Union[str, Path]],
    *,
    show_progress: bool = False,
    **kwargs,
) -> List[pd.DataFrame]:
    """Load multiple CSV files."""
    loader = lambda path: load_csv(path, **kwargs)
    return load_batch(
        paths,
        loader,
        desc="Loading CSVs",
        show_progress=show_progress,
        item_name="CSV files",
    )
