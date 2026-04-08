"""Base class for hyperparameter grid searches; extends framework GridSearchBase."""

from abc import ABC
from itertools import product
from typing import Any, Dict, List, Tuple

from level_0 import get_logger
from level_6 import GridSearchBase

logger = get_logger(__name__)


class HyperparameterGridSearchBase(GridSearchBase, ABC):
    """
    Base class for hyperparameter grid searches.

    Provides common infrastructure for hyperparameter-specific logic:
    - Parameter grid management
    - Combination generation
    - Hyperparameter application
    """

    def __init__(
        self,
        config: Any,
        grid_search_type: str,
        results_filename: str = 'results.json',
        quick_mode: bool = False,
        **kwargs
    ):
        """
        Initialize hyperparameter grid search base.

        Args:
            config: Configuration object or dict with grid_search settings.
            grid_search_type: Type identifier (e.g., 'hyperparameter').
            results_filename: Filename for results JSON (default: 'results.json').
            quick_mode: If True, use smaller parameter grid (default: False).
            **kwargs: Additional grid search parameters.
        """
        super().__init__(
            config=config,
            grid_search_type=grid_search_type,
            results_filename=results_filename,
            quick_mode=quick_mode,
            **kwargs
        )
        self.param_grid: Dict[str, List[Any]] = {}
        self.param_names: List[str] = []
        self.all_combinations: List[tuple] = []

    def setup_parameter_grid(self, param_grid: Dict[str, List[Any]]) -> Tuple[Dict[str, List[Any]], List[tuple]]:
        """
        Setup hyperparameter grid and generate all combinations.

        Args:
            param_grid: Parameter grid dictionary mapping parameter names to value lists.

        Returns:
            Tuple of (param_grid, all_combinations).
        """
        self.param_grid = param_grid
        self.param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        self.all_combinations = list(product(*param_values))

        logger.info(f"Total hyperparameter combinations: {len(self.all_combinations):,}")

        return self.param_grid, self.all_combinations

    def _generate_variant_grid(self) -> List[tuple]:
        """
        Generate the grid of hyperparameter combinations.

        Returns:
            List of hyperparameter combination tuples.
        """
        if not self.all_combinations:
            raise ValueError("Parameter grid not set. Call setup_parameter_grid() first.")
        return self.all_combinations

    def _create_variant_key_from_hyperparameters(self, variant: tuple) -> Tuple[Tuple[str, Any], ...]:
        """
        Create hyperparameter key from variant tuple.

        Args:
            variant: Hyperparameter combination tuple.

        Returns:
            Sorted tuple of (key, value) pairs from hyperparameters.
        """
        if not self.param_names:
            raise ValueError("Parameter names not set. Call setup_parameter_grid() first.")

        hyperparameters = dict(zip(self.param_names, variant))
        return tuple(sorted(hyperparameters.items()))
