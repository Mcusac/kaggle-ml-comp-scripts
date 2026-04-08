"""CSIRO-specific grid search base. Thin wrapper around ContestGridSearchBase."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_1 import ContestGridSearchBase


class CSIROGridSearchBase(ContestGridSearchBase):
    """
    CSIRO-specific grid search base class.

    Extends ContestGridSearchBase with contest_name='csiro'.
    """

    def __init__(
        self,
        config: Any,
        grid_search_type: str,
        results_filename: str = "results.json",
        quick_mode: bool = False,
        **kwargs,
    ):
        super().__init__(
            config=config,
            grid_search_type=grid_search_type,
            contest_name="csiro",
            results_filename=results_filename,
            quick_mode=quick_mode,
            **kwargs,
        )
