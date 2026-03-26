"""RNA3D train_labels.csv grouping.

Parses ID format {target_id}_{resid}, groups rows by target_id, sorts by resid.
"""

import pandas as pd


def group_labels_by_target(labels_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Group labels by target_id.

    Parses ID column (format {target_id}_{resid}) and groups rows by target_id.
    Each group is sorted by resid.

    Args:
        labels_df: Labels DataFrame with ID and resid columns.

    Returns:
        Dict mapping target_id -> group DataFrame (sorted by resid).

    Raises:
        ValueError: If required columns ID, resid are missing.
    """
    if labels_df.empty:
        return {}

    required = {"ID", "resid"}
    missing = sorted(required - set(labels_df.columns))
    if missing:
        raise ValueError(f"labels missing required columns: {missing}")

    id_series = labels_df["ID"].astype(str)
    target_prefix = id_series.str.rsplit("_", n=1).str[0]
    df = labels_df.copy()
    df["_target_id"] = target_prefix

    out: dict[str, pd.DataFrame] = {}
    for target_id, grp in df.groupby("_target_id", sort=False):
        out[str(target_id)] = grp.sort_values("resid")

    return out
