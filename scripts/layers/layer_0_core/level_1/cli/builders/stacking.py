"""
Command builder for stacking execution.
"""

from typing import List

from layers.layer_0_core.level_0 import BaseCommandBuilder


class StackingCommandBuilder(BaseCommandBuilder):

    def __init__(
        self,
        contest: str,
        base_models: List[str],
        meta_model: str,
    ):
        super().__init__()

        self.add_positional("stacking")
        self.add_option("--contest", contest)
        self.add_list_option("--base-model", base_models)
        self.add_option("--meta-model", meta_model)
