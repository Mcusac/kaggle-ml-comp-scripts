"""Aggregate train.csv from 5 rows per image to 1 row per image."""

import pandas as pd

from pathlib import Path
from typing import Union, Optional

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import get_contest

_logger = get_logger(__name__)

def aggregate_train_csv(
    train_csv_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    data_root: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Aggregate train.csv from 5 rows per image (one per target) to 1 row per image.
    
    Original format: 5 rows per image with columns: sample_id, image_path, target_name, target, ...
    Aggregated format: 1 row per image with columns: image_id, image_path, Dry_Green_g, Dry_Clover_g, ...
    
    Args:
        train_csv_path: Path to train.csv
        output_path: Optional path to save aggregated CSV
        data_root: Optional data root for constructing full image paths
        
    Returns:
        Aggregated DataFrame with one row per image
    """
    train_csv_path = Path(train_csv_path)
    
    if not train_csv_path.exists():
        raise FileNotFoundError(f"Train CSV not found: {train_csv_path}")
    
    _logger.info(f"Loading train.csv from {train_csv_path}")
    train_df = pd.read_csv(train_csv_path)
    
    # Get contest data schema
    contest = get_contest('csiro')
    data_schema = contest['data_schema']()
    config = contest['config']()
    
    # Get target columns from config
    all_targets = config.all_targets
    primary_targets = config.primary_targets
    
    # Parse sample_id using contest schema
    sample_id_col = data_schema.sample_id_column
    if sample_id_col not in train_df.columns:
        raise ValueError(f"Missing required column '{sample_id_col}' in train.csv")
    
    # Parse sample IDs
    parsed_ids = train_df[sample_id_col].apply(data_schema.parse_sample_id)
    train_df['sample_id_prefix'] = [p.get('image_id', p.get('prefix', '')) for p in parsed_ids]
    train_df['sample_id_suffix'] = [p.get('target_name', p.get('suffix', '')) for p in parsed_ids]
    
    # Verify that suffix matches target_name
    target_name_col = data_schema.target_name_column
    if target_name_col in train_df.columns:
        if not (train_df['sample_id_suffix'] == train_df[target_name_col]).all():
            _logger.warning("Some sample_id suffixes don't match target_name")
    
    # Get metadata columns from contest schema
    metadata_cols = data_schema.metadata_columns
    # Remove 'image_id' from metadata_cols for groupby
    groupby_cols = ['sample_id_prefix', data_schema.image_path_column] + [
        col for col in metadata_cols if col not in ['image_id', 'image_path']
    ]
    
    # Aggregate: pivot target values into columns
    _logger.info("Aggregating data...")
    target_name_col = data_schema.target_name_column
    target_value_col = data_schema.target_value_column
    
    # Group by metadata and pivot targets
    agg_train_df = train_df.groupby(groupby_cols).apply(
        lambda df: df.set_index(target_name_col)[target_value_col] if target_name_col in df.columns else pd.Series()
    ).reset_index()
    agg_train_df.columns.name = None
    
    # Rename sample_id_prefix to image_id for clarity
    if 'sample_id_prefix' in agg_train_df.columns:
        agg_train_df.rename(columns={'sample_id_prefix': 'image_id'}, inplace=True)
    
    # Ensure all target columns exist
    for col in all_targets:
        if col not in agg_train_df.columns:
            agg_train_df[col] = 0.0
    
    # Reorder columns: image_id, image_path, metadata, targets
    metadata_cols_ordered = [c for c in metadata_cols if c in agg_train_df.columns]
    other_cols = [col for col in agg_train_df.columns if col not in metadata_cols_ordered + all_targets]
    final_cols = ['image_id'] + [c for c in metadata_cols_ordered if c != 'image_id'] + all_targets + other_cols
    final_cols = [c for c in final_cols if c in agg_train_df.columns]
    agg_train_df = agg_train_df[final_cols]
    
    _logger.info(f"Aggregated to {len(agg_train_df)} images (from {len(train_df)} rows)")
    
    # Save if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        agg_train_df.to_csv(output_path, index=False)
        _logger.info(f"Saved aggregated CSV to {output_path}")
    
    return agg_train_df
