"""
Command builder for regression ensemble execution.
"""

from typing import List

from level_0 import BaseCommandBuilder


class RegressionEnsembleCommandBuilder(BaseCommandBuilder):

    def __init__(
        self,
        contest: str,
        models: List[str],
    ):
        super().__init__()

        self.add_positional("regression_ensemble")
        self.add_option("--contest", contest)
        self.add_list_option("--model", models)
