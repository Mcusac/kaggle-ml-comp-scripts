"""Helper functions for run.py main entry point."""

import argparse
import importlib
import os
from typing import Any, Dict, FrozenSet, Optional, Tuple

from level_0 import get_logger, setup_environment, setup_logging
from level_1 import create_config, set_seed

from layers.layer_1_competition.level_0_infra.level_1.cli_handlers_dispatch import (
    get_cli_handlers_module,
)
from layers.layer_1_competition.level_0_infra.level_1.contest.data_loading import (
    load_contest_data,
)
from layers.layer_1_competition.level_0_infra.level_1.registry import (
    ContestRegistry,
    get_contest,
)

logger = get_logger(__name__)

_KNOWN_CONTEST_SLUGS = ("arc_agi_2", "cafa", "csiro", "rna3d")


def _try_import_contest_registration(slug: str) -> None:
    try:
        importlib.import_module(
            f"layers.layer_1_competition.level_1_impl.level_{slug}.registration"
        )
    except ModuleNotFoundError:
        pass


def preload_contest_registrations(candidate_slug: Optional[str] = None) -> None:
    """Import ``registration`` so ``ContestRegistry`` is populated in subprocess CLIs.

    If ``candidate_slug`` is a known contest (e.g. from ``--contest`` or
    ``KAGGLE_COMP_CONTEST``), only that contest's registration is imported.
    Otherwise all known slugs are attempted (local multi-contest use).
    """
    key = (candidate_slug or "").strip().lower()
    if key and key in _KNOWN_CONTEST_SLUGS:
        _try_import_contest_registration(key)
        return
    for slug in _KNOWN_CONTEST_SLUGS:
        _try_import_contest_registration(slug)


def get_framework_subparser_skips(contest_name: str) -> FrozenSet[str]:
    """
    Subcommand names the framework should not register so the contest handlers
    module can own those parsers (same public CLI names, no argparse conflict).
    """
    try:
        mod = get_cli_handlers_module(contest_name)
    except ValueError:
        return frozenset()
    raw = getattr(mod, "FRAMEWORK_SUBPARSER_NAMES_TO_SKIP", None)
    if not raw:
        return frozenset()
    return frozenset(raw)


def _build_vision_config(
    contest_name: str,
    args: argparse.Namespace,
    data_root: str,
    output_dir: str,
    data_schema: Optional[Any],
) -> Any:
    """Build VisionConfig. Lives in scripts layer so orchestration does not import vision."""
    from level_0 import get_arg
    from vision import ModelConfig as VisionModelConfig, DataConfig as VisionDataConfig
    from config.training import TrainingConfig
    from config.evaluation import EvaluationConfig
    from config.paths import PathConfig
    from config.vision import VisionConfig

    num_classes = 1
    if data_schema:
        try:
            schema = data_schema() if callable(data_schema) else data_schema
            num_classes = len(schema.target_columns) if hasattr(schema, 'target_columns') else 1
        except Exception:
            pass

    model_config = VisionModelConfig(
        name=get_arg(args, 'model', 'efficientnet_b0'),
        type='vision',
        num_classes=num_classes,
        pretrained=True
    )
    data_config = VisionDataConfig(image_size=224, augmentation='medium')
    training_config = TrainingConfig(
        batch_size=get_arg(args, 'batch_size', 32),
        learning_rate=get_arg(args, 'lr', 1e-3),
        num_epochs=100
    )
    return VisionConfig(
        seed=42,
        device=get_arg(args, 'device', 'auto'),
        output_dir=output_dir,
        verbose=True,
        model=model_config,
        data=data_config,
        training=training_config,
        evaluation=EvaluationConfig(),
        paths=PathConfig(data_root=data_root, output_dir=output_dir)
    )


def _build_tabular_config(
    contest_name: str,
    args: argparse.Namespace,
    data_root: str,
    output_dir: str,
    data_schema: Optional[Any],
) -> Any:
    """Build TabularConfig. Lives in scripts layer so orchestration does not import tabular."""
    from level_0 import get_arg
    from tabular import TabularConfig, ModelConfig as TabularModelConfig, DataConfig as TabularDataConfig
    from config.training import TrainingConfig
    from config.evaluation import EvaluationConfig
    from config.paths import PathConfig

    output_dim = 1
    if data_schema:
        try:
            schema = data_schema() if callable(data_schema) else data_schema
            output_dim = len(schema.target_columns) if hasattr(schema, 'target_columns') else 1
        except Exception:
            pass
    if output_dim == 1:
        output_dim = 50

    return TabularConfig(
        seed=42,
        device=get_arg(args, 'device', 'auto'),
        output_dir=output_dir,
        verbose=True,
        model=TabularModelConfig(
            type='logistic',
            input_dim=100,
            output_dim=output_dim
        ),
        data=TabularDataConfig(),
        training=TrainingConfig(
            batch_size=get_arg(args, 'batch_size', 32),
            learning_rate=get_arg(args, 'lr', 1e-3),
            num_epochs=100
        ),
        evaluation=EvaluationConfig(),
        paths=PathConfig(
            data_root=data_root,
            output_dir=output_dir
        )
    )


def get_handler_context_builder(contest_name: str) -> Any:
    """
    Build a HandlerContextBuilder for the given contest.
    Implemented here (scripts layer) so orchestration never imports contest.

    Args:
        contest_name: Resolved contest name (e.g. 'csiro').

    Returns:
        Object implementing level_0.HandlerContextBuilder.
    """
    from level_0 import HandlerContextBuilder

    class _Builder:
        def detect_contest(self, args: argparse.Namespace) -> str:
            return contest_name

        def get_config(self, cname: str, args: argparse.Namespace) -> Any:
            return create_config(
                cname, args, get_contest=get_contest,
                get_vision_config_builder=_build_vision_config,
                get_tabular_config_builder=_build_tabular_config,
            )

        def get_paths(self, cname: str) -> Any:
            return get_contest(cname)['paths']()

        def get_data_schema(self, cname: str) -> Any:
            contest = get_contest(cname)
            data_schema = contest.get('data_schema')
            return data_schema() if data_schema else None

        def load_contest_data(
            self,
            cname: str,
            model_type: str,
            **kwargs: Any,
        ) -> Tuple[Any, Any, Any]:
            return load_contest_data(contest_name=cname, model_type=model_type, **kwargs)

    return _Builder()


def load_contest_handlers(contest_name: str, subparsers: argparse._SubParsersAction) -> Dict[str, Any]:
    """
    Load contest-specific CLI handlers.

    Args:
        contest_name: Contest name (e.g., 'csiro', 'rna3d')
        subparsers: Argument parser subparsers

    Returns:
        Dictionary of contest command handlers
    """
    contest_handlers: Dict[str, Any] = {}
    try:
        mod = get_cli_handlers_module(contest_name)
        ext = getattr(mod, 'extend_subparsers', None)
        get_h = getattr(mod, 'get_handlers', None)
        if ext is not None:
            ext(subparsers)
        if get_h is not None:
            contest_handlers = get_h() or {}
    except ValueError as e:
        logger.warning(
            "Contest CLI for %r has no registered handlers module: %s",
            contest_name, e,
        )
    except ImportError as e:
        logger.warning(
            "Contest CLI for %r could not be loaded; contest subcommands will not be available: %s",
            contest_name, e, exc_info=True
        )
    except AttributeError as e:
        logger.warning(
            "Contest CLI for %r is missing extend_subparsers or get_handlers: %s",
            contest_name, e, exc_info=True
        )
    return contest_handlers


def setup_logging_and_environment(args: argparse.Namespace) -> None:
    """Set up logging, environment, and random seed."""
    setup_logging(getattr(args, "log_level", None))
    model = getattr(args, "model_name", None) or getattr(args, "model", None)
    setup_environment(
        model,
        getattr(args, "download_weights", True),
    )
    set_seed(getattr(args, "seed", 42))


def resolve_contest(early_contest: Optional[str]) -> str:
    """Resolve contest from early --contest, KAGGLE_COMP_CONTEST, or auto-detect."""
    if early_contest:
        return early_contest
    available = ContestRegistry.list_contests()
    env = os.environ.get("KAGGLE_COMP_CONTEST", "").strip()
    if env:
        if env in available:
            return env
        raise ValueError(
            "KAGGLE_COMP_CONTEST=%r is not a registered contest. Registered: %s"
            % (env, ", ".join(sorted(available)))
        )
    if len(available) == 1:
        return available[0]
    if len(available) > 1:
        raise ValueError(
            "Multiple contests available; set --contest or KAGGLE_COMP_CONTEST. "
            f"Available: {available}"
        )
    raise ValueError(
        "No contest specified and none registered. "
        "Set --contest or KAGGLE_COMP_CONTEST, or register a contest."
    )
