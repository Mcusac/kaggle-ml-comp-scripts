"""
Framework-agnostic export verification.
"""

from pathlib import Path
from typing import Union, Dict, Optional


def _make_result(
    success: bool,
    message: str,
    model_path: Optional[Path],
) -> Dict[str, Union[bool, str, Optional[Path]]]:
    """Build standardized verification result dict."""
    return {'success': success, 'message': message, 'model_path': model_path}


def verify_export_files(export_dir: Union[str, Path], model_type: str = 'end_to_end') -> Dict[str, Union[bool, str, Optional[Path]]]:
    """
    Verify existence of exported model files in a given directory.
    
    Args:
        export_dir: Directory containing exported models
        model_type: Type of model ('end_to_end', 'regression', or 'any')
        
    Returns:
        Dict with keys:
            - success: bool
            - message: str
            - model_path: Path or None
    """
    export_dir = Path(export_dir)
    
    if not export_dir.exists():
        return _make_result(False, f"Export directory not found: {export_dir}", None)

    if model_type == 'end_to_end':
        model_path = export_dir / 'best_model.pth'
        if model_path.exists():
            return _make_result(True, 'Export successful!', model_path)
        return _make_result(False, 'End-to-end model not found', None)

    if model_type == 'regression':
        regression_model = export_dir / 'regression_model.pkl'
        end_to_end_model = export_dir / 'best_model.pth'
        if regression_model.exists():
            return _make_result(True, 'Regression model export successful!', regression_model)
        if end_to_end_model.exists():
            return _make_result(True, 'End-to-end model fallback found', end_to_end_model)
        return _make_result(False, 'No expected model files found', None)

    # model_type == 'any'
    candidates = [export_dir / 'best_model.pth', export_dir / 'regression_model.pkl']
    for p in candidates:
        if p.exists():
            return _make_result(True, 'Model file found', p)
    return _make_result(False, 'No model files found', None)