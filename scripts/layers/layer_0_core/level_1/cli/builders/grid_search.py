"""
Command builder for grid search execution.
"""

from typing import Optional

from level_0 import BaseCommandBuilder


class GridSearchCommandBuilder(BaseCommandBuilder):

    def __init__(
        self,
        contest: str,
        config: str,
        search_type: Optional[str] = None,
        fold: Optional[int] = None,
    ):
        super().__init__()

        self.add_positional("grid_search")
        self.add_option("--contest", contest)
        self.add_option("--config", config)
        self.add_option("--search-type", search_type)
        self.add_option("--fold", fold)
