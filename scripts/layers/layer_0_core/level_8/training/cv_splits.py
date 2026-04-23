"""CV split creation: visual clustering and hierarchical stratification."""

import numpy as np
import pandas as pd

from typing import Dict, List, Optional

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def create_robust_cv_splits(
    data: 'pd.DataFrame',
    target_names: List[str],
    target_weights: Dict[str, float],
    embedding_cols: Optional[List[str]] = None,
    n_splits: int = 5,
    n_clusters: int = 30,
    seed: int = 42,
    use_hierarchical: bool = False
) -> 'pd.DataFrame':
    """
    Create robust CV splits using visual clustering and stratification.

    Uses embeddings to create visual clusters, then uses StratifiedGroupKFold
    to ensure similar images don't leak between train/val.

    Alternative: Uses hierarchical stratification (State → Total Mass → Clover Fraction)
    if use_hierarchical=True.

    Args:
        data: DataFrame with embeddings and targets
        target_names: List of target column names
        target_weights: Dictionary mapping target names to weights
        embedding_cols: List of embedding column names. If None, auto-detects columns
                       starting with 'emb' or numeric columns.
        n_splits: Number of CV folds (default: 5)
        n_clusters: Number of visual clusters (default: 30)
        seed: Random seed (default: 42)
        use_hierarchical: If True, use hierarchical stratification instead of visual clustering

    Returns:
        DataFrame with added 'fold' column
    """
    df = data.copy()

    if use_hierarchical:
        return _create_hierarchical_cv_splits(df, target_names, n_splits, seed)

    if embedding_cols is None:
        emb_cols = [c for c in df.columns if "emb" in str(c).lower()]
        if not emb_cols:
            exclude = set(target_names + list(target_weights.keys()) +
                          ['fold', 'id', 'image_path', 'State', 'Species', 'image_id'])
            emb_cols = [c for c in df.columns if c not in exclude and str(c).isdigit()]

    if not emb_cols:
        raise ValueError("No embedding columns found. Provide embedding_cols or ensure columns start with 'emb'")

    _logger.info(f"Using {len(emb_cols)} embedding columns for clustering")

    pca = PCA(n_components=0.85, random_state=seed)
    X_emb = pca.fit_transform(df[emb_cols].values)

    kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    df["visual_cluster"] = kmeans.fit_predict(X_emb)

    composite = np.zeros(len(df))
    for t in target_names:
        if t in df.columns:
            composite += df[t] * target_weights.get(t, 0.0)

    try:
        df['target_bins'] = pd.qcut(composite, q=10, labels=False, duplicates='drop')
    except ValueError:
        df['target_bins'] = pd.qcut(composite, q=5, labels=False, duplicates='drop')

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    df["fold"] = -1
    for fold, (train_idx, val_idx) in enumerate(
        sgkf.split(df, df['target_bins'], groups=df["visual_cluster"])
    ):
        df.loc[val_idx, "fold"] = fold

    leakage_check = df.groupby('visual_cluster')['fold'].nunique()
    leakage_count = sum(leakage_check > 1)
    if leakage_count > 0:
        _logger.warning(f"Warning: {leakage_count} clusters appear in multiple folds")
    else:
        _logger.info("No leakage detected: all clusters in single fold")

    return df


def _create_hierarchical_cv_splits(
    df: 'pd.DataFrame',
    target_names: List[str],
    n_splits: int,
    seed: int
) -> 'pd.DataFrame':
    """
    Create CV splits using hierarchical stratification.

    Hierarchy: State → Total Mass → Clover Fraction
    Falls back to simpler levels if bins are too rare.
    """
    df = df.copy().reset_index(drop=True)

    if 'Dry_Total_g' in df.columns:
        df['bin_total'] = pd.qcut(df['Dry_Total_g'], q=3, labels=["L", "M", "H"])
    else:
        df['bin_total'] = "M"

    if 'Dry_Clover_g' in df.columns and 'Dry_Green_g' in df.columns:
        living_mass = df['Dry_Clover_g'] + df['Dry_Green_g']
        df['clover_frac'] = df['Dry_Clover_g'] / (living_mass + 1e-6)
        df['bin_clover'] = pd.cut(df['clover_frac'], bins=[-0.1, 0.2, 1.1], labels=["Lo", "Hi"])
    else:
        df['bin_clover'] = "Lo"

    if 'State' in df.columns:
        df['state_key'] = df['State'].astype(str)
    else:
        df['state_key'] = "Unknown"

    df['key_L1'] = df['state_key'] + "_" + df['bin_total'].astype(str) + "_" + df['bin_clover'].astype(str)
    df['key_L2'] = df['state_key'] + "_" + df['bin_total'].astype(str)
    df['key_L3'] = df['state_key']

    df['final_stratify'] = df['key_L1']

    counts = df['final_stratify'].value_counts()
    rare_keys = counts[counts < n_splits].index

    mask_rare_L1 = df['final_stratify'].isin(rare_keys)
    df.loc[mask_rare_L1, 'final_stratify'] = df.loc[mask_rare_L1, 'key_L2']

    counts = df['final_stratify'].value_counts()
    rare_keys = counts[counts < n_splits].index

    mask_rare_L2 = df['final_stratify'].isin(rare_keys)
    df.loc[mask_rare_L2, 'final_stratify'] = df.loc[mask_rare_L2, 'key_L3']

    counts = df['final_stratify'].value_counts()
    rare_keys = counts[counts < n_splits].index
    if len(rare_keys) > 0:
        _logger.warning(f"Dropping {len(rare_keys)} extremely rare buckets to 'Misc'")
        df.loc[df['final_stratify'].isin(rare_keys), 'final_stratify'] = 'Misc'

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    df['fold'] = -1
    for fold, (train_idx, val_idx) in enumerate(skf.split(df, df['final_stratify'])):
        df.loc[val_idx, 'fold'] = fold

    return df
