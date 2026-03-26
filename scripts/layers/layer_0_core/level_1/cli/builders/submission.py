"""
Command builder for submission generation.
"""

from typing import Optional

from level_0 import BaseCommandBuilder


class SubmissionCommandBuilder(BaseCommandBuilder):

    def __init__(
        self,
        contest: str,
        model: str,
        tta: bool = False,
        output: Optional[str] = None,
    ):
        super().__init__()

        self.add_positional("submit")
        self.add_option("--contest", contest)
        self.add_option("--model", model)
        self.add_flag("--tta", tta)
        self.add_option("--output", output)
