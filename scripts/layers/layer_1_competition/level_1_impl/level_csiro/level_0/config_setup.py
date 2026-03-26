"""Contest config setup for train-and-export pipeline."""

from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import get_pretrained_weights_path
from layers.layer_1_competition.level_0_infra.level_1 import get_contest


def setup_contest_config(
    feature_extraction_mode: bool,
    feature_extraction_model: Optional[str],
    regression_model_type: Optional[str],
    dataset_type: str,
):
    """Setup and configure contest config object."""
    contest = get_contest("csiro")
    contest_config = contest["config"]()

    if not hasattr(contest_config, "model"):
        class ModelConfig:
            def __init__(self):
                self.feature_extraction_mode = False
                self.feature_extraction_model_name = None
                self.regression_model_type = None

        contest_config.model = ModelConfig()

    if not hasattr(contest_config, "data"):
        class DataConfig:
            def __init__(self):
                self.dataset_type = "split"

        contest_config.data = DataConfig()

    if feature_extraction_mode:
        contest_config.model.feature_extraction_mode = True
        if feature_extraction_model:
            pretrained_path_or_name = get_pretrained_weights_path(feature_extraction_model)
            contest_config.model.feature_extraction_model_name = pretrained_path_or_name
        if regression_model_type:
            contest_config.model.regression_model_type = regression_model_type
        if dataset_type:
            contest_config.data.dataset_type = dataset_type

    return contest_config
