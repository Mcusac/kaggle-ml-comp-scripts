"""
Command builder for train/export execution.
"""

from typing import Optional

from level_0 import BaseCommandBuilder


class TrainExportCommandBuilder(BaseCommandBuilder):

    def __init__(
        self,
        contest: str,
        config: str,
        fold: Optional[int] = None,
        export: bool = False,
        device: Optional[str] = None,
    ):
        super().__init__()

        self.add_positional("train_export")
        self.add_option("--contest", contest)
        self.add_option("--config", config)
        self.add_option("--fold", fold)
        self.add_option("--device", device)
        self.add_flag("--export", export)
