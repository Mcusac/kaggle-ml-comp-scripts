"""Test (inference-only) pipeline for CSIRO contest."""

import torch
import numpy as np
import pandas as pd

from pathlib import Path
from typing import Optional, Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import get_device, cleanup_gpu_memory
from layers.layer_0_core.level_5 import save_submission_csv
from layers.layer_0_core.level_6 import create_streaming_test_dataloader

from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model
from layers.layer_1_competition.level_0_infra.level_5 import (
    expand_predictions_to_submission_format,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import load_model_from_checkpoint

logger = get_logger(__name__)


def test_pipeline(
    contest_context: Any,
    data_root: Optional[str] = None,
    model_path: Optional[str] = None,
    test_filename: str = 'test.csv',
    batch_size: Optional[int] = None,
    dataset_type: str = 'split',
    model_name: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Run inference-only pipeline with TTA support. Contest passes contest_context.
    """
    paths = contest_context.get_paths()
    config = contest_context.get_config()
    data_schema = getattr(contest_context, 'get_data_schema', lambda: None)()
    post_processor = getattr(contest_context, 'get_post_processor', lambda: None)()

    if batch_size is None:
        batch_size = config.default_batch_size
    if data_root is None:
        data_root = str(paths.get_data_root())

    test_csv_path = str(Path(data_root) / test_filename)

    device = get_device('auto')

    if model_path:
        logger.info(f"Loading model from checkpoint: {model_path}")

        checkpoint_preview = torch.load(model_path, map_location=device, weights_only=False)
        if model_name is None:
            model_name = checkpoint_preview.get('model_name', config.default_feature_extraction_model)

        model = create_feature_extraction_model(
            model_name=model_name,
            num_primary_targets=len(config.primary_targets),
            device=device,
            image_size=None,
            pretrained=False
        )

        checkpoint_meta = load_model_from_checkpoint(
            model=model,
            path=Path(model_path),
            device=device
        )

        model.to(device)
        model.eval()
    else:
        raise ValueError("model_path is required for test_pipeline")

    image_size = model.get_input_size() if hasattr(model, 'get_input_size') else config.default_image_size

    test_loader = create_streaming_test_dataloader(
        test_csv_path=test_csv_path,
        data_root=data_root,
        image_path_column=data_schema.image_path_column,
        primary_targets=config.primary_targets,
        image_size=image_size,
        batch_size=batch_size,
        dataset_type=dataset_type,
        num_workers=0
    )

    logger.info("Running inference...")
    all_predictions = []

    with torch.no_grad():
        for batch in test_loader:
            if dataset_type == 'split':
                left_img, right_img, _ = batch
                left_img = left_img.to(device)
                right_img = right_img.to(device)
                outputs = model((left_img, right_img))
            else:
                images, _ = batch
                images = images.to(device)
                outputs = model(images)

            all_predictions.append(outputs.cpu().numpy())

    predictions = np.concatenate(all_predictions, axis=0)

    del model
    cleanup_gpu_memory()

    logger.info("Expanding predictions to submission format...")
    submission_df = expand_predictions_to_submission_format(
        predictions=predictions,
        test_csv_path=test_csv_path,
        contest_config=config,
        data_schema=data_schema,
        post_processor=post_processor
    )

    output_path = str(paths.get_output_dir() / 'submission.csv')
    save_submission_csv(submission_df, output_path=output_path)

    logger.info(f"✅ Inference complete. Submission saved to {output_path}")

    return submission_df
