"""Generic metadata path helpers for Kaggle competitions and local mimic layouts."""

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import is_kaggle, ensure_dir
from layers.layer_0_core.level_4 import load_json


def _find_project_input_root(from_file: str) -> Optional[Path]:
    """Find project root that contains 'input/' (local mimic layout)."""
    try:
        for p in Path(from_file).resolve().parents:
            if (p / "input").is_dir():
                return p / "input"
    except Exception:
        pass
    return None


def _find_project_working_root(from_file: str) -> Optional[Path]:
    """Find project root that contains 'working/' (local mimic layout)."""
    try:
        for p in Path(from_file).resolve().parents:
            if (p / "working").is_dir():
                return p / "working"
        return None
    except Exception:
        pass
    return None


def find_metadata_dir(
    dataset_name: str,
    from_file: Optional[str] = None,
) -> Optional[Path]:
    """
    Find the metadata directory for reading.

    Order: /kaggle/input/{dataset_name}, /kaggle/working/{dataset_name},
    then local mimic input/{dataset_name}, else ../{dataset_name}.

    Args:
        dataset_name: Name of the metadata dataset (e.g. 'csiro-metadata').
        from_file: Path used for project-root discovery. Defaults to this module's __file__.

    Returns:
        Path to metadata directory if found, else None.
    """
    ref = from_file if from_file is not None else __file__
    if is_kaggle():
        for candidate in [
            Path(f"/kaggle/input/{dataset_name}"),
            Path(f"/kaggle/working/{dataset_name}"),
        ]:
            if candidate.exists():
                return candidate
    else:
        inp = _find_project_input_root(ref)
        if inp is not None:
            candidate = inp / dataset_name
            if candidate.exists():
                return candidate
        local = Path(f"../{dataset_name}").resolve()
        if local.exists():
            return local
    return None


def get_writable_metadata_dir(
    dataset_name: str,
    from_file: Optional[str] = None,
) -> Path:
    """
    Get the writable metadata directory. Creates it if missing.

    Kaggle: /kaggle/working/{dataset_name}.
    Local mimic: working/{dataset_name} when project has working/; else ../{dataset_name}.

    Args:
        dataset_name: Name of the metadata dataset (e.g. 'csiro-metadata').
        from_file: Path used for project-root discovery. Defaults to this module's __file__.

    Returns:
        Path to writable metadata directory.
    """
    ref = from_file if from_file is not None else __file__
    if is_kaggle():
        d = Path(f"/kaggle/working/{dataset_name}")
    else:
        wrk = _find_project_working_root(ref)
        if wrk is not None:
            d = wrk / dataset_name
        else:
            d = Path(f"../{dataset_name}").resolve()
    ensure_dir(d)
    return d


def load_combo_metadata(metadata_dir: Path, subpath: str) -> dict:
    """
    Load combo metadata JSON from metadata_dir / subpath.

    Args:
        metadata_dir: Base metadata directory.
        subpath: Relative path to metadata JSON (e.g. 'data_manipulation/metadata.json').

    Returns:
        Parsed JSON as dict.
    """
    path = metadata_dir / subpath
    return load_json(path)
