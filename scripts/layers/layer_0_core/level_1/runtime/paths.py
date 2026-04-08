"""Environment-aware path resolution.

Provides path resolution that adapts to execution environment
(Kaggle vs local) while remaining generic (not contest-specific).
"""

import os

from pathlib import Path
from typing import Dict, Union, Optional

from level_0 import EnvironmentConfigError, is_kaggle

def get_environment_type() -> str:
    """
    Get the current execution environment type.
    
    Returns:
        'kaggle' or 'local'
        
    Example:
        >>> env = get_environment_type()
        >>> print(f"Running in {env} environment")
    """
    return 'kaggle' if is_kaggle() else 'local'


def get_environment_paths() -> Dict[str, Path]:
    """
    Get standard paths for the current environment.
    
    Returns:
        Dictionary mapping path purposes to actual paths:
        - 'working': Current working directory
        - 'data': Data input directory
        - 'output': Output directory
        - 'temp': Temporary directory
        
    Example:
        >>> paths = get_environment_paths()
        >>> data_dir = paths['data']
        >>> output_dir = paths['output']
    """
    if is_kaggle():
        return {
            'working': Path(os.getenv('KAGGLE_WORKING_DIR', '/kaggle/working')),
            'data': Path(os.getenv('KAGGLE_INPUT_DIR', '/kaggle/input')),
            'output': Path(os.getenv('KAGGLE_OUTPUT_DIR', '/kaggle/working')),
            'temp': Path(os.getenv('KAGGLE_TEMP_DIR', '/kaggle/temp')),
        }
    else:
        return {
            'working': Path.cwd(),
            'data': Path('data'),
            'output': Path('output'),
            'temp': Path('temp'),
        }


def get_environment_root(purpose: str = 'output') -> Path:
    """
    Get the root directory for a specific purpose.
    
    Args:
        purpose: One of 'working', 'data', 'output', 'temp'
        
    Returns:
        Path object for the requested root
        
    Raises:
        EnvironmentConfigError: If purpose is not recognized
        
    Example:
        >>> output_root = get_environment_root('output')
        >>> model_path = output_root / 'models' / 'best.pkl'
    """
    paths = get_environment_paths()
    if purpose not in paths:
        raise EnvironmentConfigError(
            f"Unknown purpose '{purpose}'. "
            f"Valid options: {list(paths.keys())}"
        )
    return paths[purpose]


def resolve_environment_path(
    relative_path: Union[str, Path],
    purpose: str = 'output'
) -> Path:
    """
    Resolve a relative path against environment root.
    
    Args:
        relative_path: Relative path from root
        purpose: Root directory purpose (default: 'output')
        
    Returns:
        Absolute path in current environment
        
    Example:
        >>> # In Kaggle: /kaggle/working/models/best.pkl
        >>> # Locally: output/models/best.pkl
        >>> path = resolve_environment_path('models/best.pkl')
    """
    root = get_environment_root(purpose)
    return root / relative_path


def resolve_path(
    path: Union[str, Path],
    kaggle_path: Optional[Union[str, Path]] = None
) -> Path:
    """
    Resolve path based on environment with optional override.
    
    If kaggle_path is provided and running in Kaggle, use it.
    Otherwise use the default path.
    
    Args:
        path: Default path (for local)
        kaggle_path: Optional Kaggle-specific path
        
    Returns:
        Resolved Path object
        
    Example:
        >>> # Use different paths per environment
        >>> data_path = resolve_path('data/train.csv', '/kaggle/input/comp/train.csv')
    """
    if is_kaggle() and kaggle_path is not None:
        return Path(kaggle_path)
    return Path(path)


def get_kaggle_working_submission_csv_path() -> Path:
    """
    Return the canonical Kaggle working-dir submission path.
    """
    return Path(os.getenv('KAGGLE_WORKING_DIR', '/kaggle/working')) / "submission.csv"


def get_default_submission_csv_path(*, purpose: str = "output") -> Path:
    """
    Return the default environment-specific submission CSV path.

    - Kaggle: /kaggle/working/submission.csv (or KAGGLE_WORKING_DIR override)
    - Local: <output-root>/submission.csv
    """
    if is_kaggle():
        return get_kaggle_working_submission_csv_path()
    return resolve_environment_path("submission.csv", purpose=purpose)