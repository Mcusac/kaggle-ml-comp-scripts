"""Contest-aware grid search base extending framework GridSearchBase."""

from typing import Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_6 import GridSearchBase

from layers.layer_1_competition.level_0_infra.level_1.registry import get_contest

logger = get_logger(__name__)


class ContestGridSearchBase(GridSearchBase):
    """
    Contest-aware grid search base.

    Injects contest paths and config. Subclasses pass contest_name.
    """

    def __init__(
        self,
        config: Any,
        grid_search_type: str,
        contest_name: str,
        results_filename: str = "results.json",
        quick_mode: bool = False,
        **kwargs,
    ):
        """
        Initialize with contest context.

        Args:
            config: Configuration (dict or object). If dict, merged with contest config.
            grid_search_type: Type identifier for this grid search (e.g. 'hyperparameter')
            contest_name: Registered contest name (e.g. 'csiro')
            results_filename: Filename for results JSON
            quick_mode: Use smaller parameter grid
            **kwargs: Passed to GridSearchBase
        """
        contest = get_contest(contest_name)
        paths = contest["paths"]()
        contest_config = contest["config"]()

        if isinstance(config, dict):
            merged_config = contest_config
            for key, value in config.items():
                if hasattr(merged_config, key):
                    setattr(merged_config, key, value)
            config = merged_config

        if not hasattr(config, "paths"):
            class _SimplePaths:
                def __init__(self, paths_obj):
                    self.output_dir = paths_obj.get_output_dir()
                    self.model_dir = paths_obj.get_models_base_dir()

            config.paths = _SimplePaths(paths)

        super().__init__(
            config=config,
            grid_search_type=grid_search_type,
            results_filename=results_filename,
            quick_mode=quick_mode,
            **kwargs,
        )
        self.contest = contest
        self.contest_paths = paths
        self.contest_config = contest_config
        self._contest_name = contest_name
