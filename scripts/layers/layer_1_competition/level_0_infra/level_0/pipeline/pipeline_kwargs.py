"""Utilities for creating pipeline/workflow kwargs."""
# CANDIDATE: could be more general and then call and wrap it for machine learning (ie the model_type)

from typing import Any, Optional

def create_pipeline_kwargs(
    paths: Any,
    data_schema: Any,
    model_type: str,
    image_subdir: Optional[str] = "images",
) -> dict:
    """
    Create common kwargs for pipeline/workflow creation.

    Args:
        paths: Contest paths object
        data_schema: Contest data schema
        model_type: Model type
        image_subdir: Subdirectory under data root for images. Default "images".
            Pass None to omit image_dir (contests without image data).

    Returns:
        Dictionary of common kwargs
    """
    kwargs = {
        "model_type": model_type,
    }

    if image_subdir is not None and hasattr(paths, "local_data_root"):
        kwargs["image_dir"] = str(paths.local_data_root / image_subdir)

    if data_schema and hasattr(data_schema, 'target_columns'):
        kwargs['target_cols'] = data_schema.target_columns

    return kwargs
