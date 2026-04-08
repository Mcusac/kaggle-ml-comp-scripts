"""Contest registry for auto-detection and management."""

import argparse
import os

from typing import Any, Callable, Dict, Type, Optional

from layers.layer_0_core.level_0 import get_arg
from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import (
    ContestConfig,
    ContestDataSchema,
    ContestPaths,
    ContestPostProcessor,
    register_model_id_map,
)

logger = get_logger(__name__)


class ContestRegistry:
    """Registry for contest implementations."""

    _contests: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        config: Type[ContestConfig],
        data_schema: Type[ContestDataSchema],
        paths: Type[ContestPaths],
        post_processor: Type[ContestPostProcessor],
        training_data_loader: Optional[Callable] = None,
    ) -> None:
        """
        Register a contest implementation.

        Args:
            name: Contest name (e.g., 'csiro', 'cafa')
            config: ContestConfig implementation
            data_schema: ContestDataSchema implementation
            paths: ContestPaths implementation
            post_processor: ContestPostProcessor implementation
            training_data_loader: Optional callable(Path) -> DataFrame for contest-specific train CSV loading
        """
        entry = {
            'config': config,
            'data_schema': data_schema,
            'paths': paths,
            'post_processor': post_processor,
        }
        if training_data_loader is not None:
            entry['training_data_loader'] = training_data_loader
        cls._contests[name] = entry

    @classmethod
    def get(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Get contest implementation by name.

        Args:
            name: Contest name

        Returns:
            Dict with contest classes, or None if not found
        """
        return cls._contests.get(name)

    @classmethod
    def list_contests(cls) -> list:
        """
        List all registered contests.

        Returns:
            List of contest names
        """
        return list(cls._contests.keys())


def register_contest(
    name: str,
    config: Type[ContestConfig],
    data_schema: Type[ContestDataSchema],
    paths: Type[ContestPaths],
    post_processor: Type[ContestPostProcessor],
    training_data_loader: Optional[Callable] = None,
) -> None:
    """
    Register a contest implementation.

    Args:
        name: Contest name
        config: ContestConfig implementation
        data_schema: ContestDataSchema implementation
        paths: ContestPaths implementation
        post_processor: ContestPostProcessor implementation
        training_data_loader: Optional callable(Path) -> DataFrame for contest-specific train CSV loading
    """
    ContestRegistry.register(
        name, config, data_schema, paths, post_processor,
        training_data_loader=training_data_loader,
    )


def get_contest(name: str) -> Dict[str, Type]:
    """
    Get contest implementation by name.

    Args:
        name: Contest name

    Returns:
        Dict with contest classes

    Raises:
        ValueError: If contest not found
    """
    contest = ContestRegistry.get(name)
    if contest is None:
        available = ContestRegistry.list_contests()
        raise ValueError(
            f"Contest '{name}' not found. Available contests: {available}"
        )
    return contest


def detect_contest(args: argparse.Namespace) -> str:  # only used in cli/handlers.py (setup_handler_context)
    """
    Detect contest from arguments or environment.
    Precedence: args.contest, KAGGLE_COMP_CONTEST (when set and registered), else
    the only registered contest; else raise.
    """
    contest = get_arg(args, 'contest')
    if contest:
        return contest

    available = ContestRegistry.list_contests()
    env = os.environ.get("KAGGLE_COMP_CONTEST", "").strip()
    if env and env in available:
        return env
    if env and env not in available:
        raise ValueError(
            "KAGGLE_COMP_CONTEST=%r is not a registered contest. "
            "Registered: %s" % (env, ", ".join(sorted(available)))
        )
    if len(available) == 1:
        logger.info(f"Auto-detected contest: {available[0]}")
        return available[0]
    if len(available) > 1:
        raise ValueError(
            "Multiple contests available; set --contest or KAGGLE_COMP_CONTEST. Available: %s"
            % available
        )
    raise ValueError("No contests registered. Please register a contest implementation.")


# Default model-name → ID map for core feature-cache naming. Contests that call
# set_model_id_map (e.g. CSIRO registration) run after level_1 loads and replace this.
register_model_id_map()
