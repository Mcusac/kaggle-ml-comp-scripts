"""
Command builder for ensemble execution.
"""

from typing import List, Optional

from layers.layer_0_core.level_0 import BaseCommandBuilder


class EnsembleCommandBuilder(BaseCommandBuilder):

    def __init__(
        self,
        contest: str,
        models: List[str],
        method: Optional[str] = None,
    ):
        super().__init__()

        self.add_positional("ensemble")
        self.add_option("--contest", contest)
        self.add_list_option("--model", models)
        self.add_option("--method", method)
