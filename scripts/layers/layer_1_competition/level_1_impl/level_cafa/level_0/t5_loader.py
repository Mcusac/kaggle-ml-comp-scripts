"""Load T5 embeddings from R data formats (.rds, .qs)."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, Tuple

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def load_t5_rds(rds_path: Path, datatype: str, use_memmap: bool) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load T5 embeddings from .rds file (R data format).

    Args:
        rds_path: Path to .rds file
        datatype: 'train' or 'test'
        use_memmap: Whether to use memory mapping (not supported for .rds, will load full array)

    Returns:
        (embeddings_array, ids_array)
    """
    _logger.info(f"Loading T5 {datatype} embeddings from .rds file: {rds_path}")

    try:
        import pyreadr
    except ImportError as e:
        raise ImportError(
            "pyreadr is required to load T5 .rds files. Install with: pip install pyreadr"
        ) from e

    try:
        result = pyreadr.read_r(str(rds_path))

        if not result:
            raise ValueError(f"No data found in .rds file: {rds_path}")

        data_key = list(result.keys())[0]
        data = result[data_key]
    except Exception as e:
        raise IOError(
            f"Failed to load .rds file with pyreadr: {e}\n"
            f"Consider using .qs files instead or install R and rpy2 for .rds support."
        ) from e

    if hasattr(data, 'index') and hasattr(data, 'values'):
        if isinstance(data.index, pd.Index):
            ids = data.index.tolist()
            embeds = data.values
        elif len(data.columns) > 0 and data.columns[0] in ['protein_id', 'id', 'ID', 'Protein_ID']:
            ids = data.iloc[:, 0].tolist()
            embeds = data.iloc[:, 1:].values
        else:
            ids = data.iloc[:, 0].astype(str).tolist()
            embeds = data.iloc[:, 1:].values
    else:
        raise ValueError(
            f"Unexpected data structure in .rds file. "
            f"Expected DataFrame with protein IDs. Got: {type(data)}"
        )

    embeds = np.asarray(embeds, dtype=np.float32)
    ids = np.asarray(ids, dtype=str)

    _logger.info(f"Loaded T5 {datatype}: {embeds.shape} (dtype: {embeds.dtype}), IDs: {len(ids)}")

    if use_memmap:
        _logger.info("Memory mapping not supported for .rds files, loaded full array")

    return embeds, ids


def load_t5_qs(qs_path: Path, datatype: str, use_memmap: bool) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load T5 embeddings from .qs file (compressed R data format).

    Args:
        qs_path: Path to .qs file
        datatype: 'train' or 'test'
        use_memmap: Whether to use memory mapping (not supported for .qs, will load full array)

    Returns:
        (embeddings_array, ids_array)
    """
    _logger.info(f"Loading T5 {datatype} embeddings from .qs file: {qs_path}")

    data = _load_qs_file_via_r(qs_path)
    data = _validate_and_convert_dataframe(data)
    ids, embeds = _extract_ids_and_embeddings(data)

    embeds = np.asarray(embeds, dtype=np.float32)
    ids = np.asarray(ids, dtype=str)

    _logger.info(f"Loaded T5 {datatype}: {embeds.shape} (dtype: {embeds.dtype}), IDs: {len(ids)}")

    if use_memmap:
        _logger.info("Memory mapping not supported for .qs files, loaded full array")

    return embeds, ids


def _load_qs_file_via_r(qs_path: Path) -> pd.DataFrame:
    """Load .qs file using R's qs package via rpy2."""
    try:
        import rpy2.robjects as ro
        from rpy2.robjects import pandas2ri

        pandas2ri.activate()

        ro.r('if (!require("qs", quietly=TRUE)) install.packages("qs", repos="https://cloud.r-project.org")')
        ro.r(f'data <- qs::qread("{qs_path}")')
        r_data = ro.r('data')

        data = pandas2ri.rpy2py(r_data)
        _logger.info("Loaded using rpy2 + R qs package (converted to pandas DataFrame)")
        return data
    except ImportError:
        raise ImportError(
            "rpy2 library required for loading T5 .qs files. "
            "Install with: pip install rpy2\n"
            "Note: R must also be installed on the system."
        )
    except Exception as e:
        raise IOError(
            f"Failed to load .qs file using rpy2: {e}\n"
            f"Make sure R is installed and the 'qs' R package is available.\n"
            f"Alternatively, convert .qs files to .npy format for faster loading."
        ) from e


def _validate_and_convert_dataframe(data: Any) -> pd.DataFrame:
    """Validate and convert data to pandas DataFrame."""
    if not isinstance(data, pd.DataFrame):
        try:
            from rpy2.robjects import pandas2ri

            data = pandas2ri.rpy2py(data)
        except Exception:
            raise ValueError(
                f"Unexpected data structure in .qs file. "
                f"Expected DataFrame. Got: {type(data)}"
            )

    if len(data) == 0:
        raise ValueError("Empty DataFrame in .qs file")

    return data


def _extract_ids_and_embeddings(data: pd.DataFrame) -> Tuple[list, np.ndarray]:
    """Extract IDs and embeddings from DataFrame using multiple strategies."""
    if not pd.api.types.is_numeric_dtype(data.index):
        return _extract_from_index(data)

    if len(data.columns) > 0 and str(data.columns[0]).lower() in ['protein_id', 'id', 'protein', 'proteinid']:
        return _extract_from_first_column(data)

    if len(data.columns) > 0 and pd.api.types.is_object_dtype(data.iloc[:, 0]):
        first_col_sample = data.iloc[:min(10, len(data)), 0]
        if first_col_sample.dtype == 'object' and not pd.api.types.is_numeric_dtype(first_col_sample):
            return _extract_from_first_column(data)

    return _extract_from_index(data)


def _extract_from_index(data: pd.DataFrame) -> Tuple[list, np.ndarray]:
    """Extract IDs from index and embeddings from numeric columns."""
    ids = data.index.astype(str).tolist()
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    embeds = data[numeric_cols].values
    return ids, embeds


def _extract_from_first_column(data: pd.DataFrame) -> Tuple[list, np.ndarray]:
    """Extract IDs from first column and embeddings from remaining numeric columns."""
    ids = data.iloc[:, 0].astype(str).tolist()
    embed_cols = data.iloc[:, 1:]
    numeric_cols = embed_cols.select_dtypes(include=[np.number]).columns
    embeds = embed_cols[numeric_cols].values
    return ids, embeds
