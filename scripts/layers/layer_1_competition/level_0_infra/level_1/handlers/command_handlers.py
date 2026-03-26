"""Command handlers for CLI routing. Orchestration does not import contest."""

import argparse
import numpy as np

from typing import Dict, Callable, Any
from pathlib import Path

from layers.layer_0_core.level_0 import Command, get_arg, parse_comma_separated, ensure_dir, get_logger
from layers.layer_0_core.level_2 import simple_average
from layers.layer_0_core.level_6 import PredictPipeline
from layers.layer_0_core.level_5 import ExportPipeline
from layers.layer_0_core.level_8 import TrainPipeline
from layers.layer_0_core.level_9 import CrossValidateWorkflow, HyperparameterGridSearch, TrainPredictWorkflow

from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs

logger = get_logger(__name__)


def _setup_handler_context(
    args: argparse.Namespace,
    builder: Any,
) -> tuple[str, Any, str, Any, Any, Any]:
    """Set up common context for command handlers using injected builder."""
    contest_name = builder.detect_contest(args)
    config = builder.get_config(contest_name, args)
    model_type = get_arg(args, 'model_type', 'vision')
    config.model.type = model_type
    data_schema = builder.get_data_schema(contest_name)
    paths = builder.get_paths(contest_name)
    contest = {'paths': lambda: paths, 'data_schema': lambda: data_schema}
    return contest_name, config, model_type, contest, data_schema, paths


def _make_handlers(builder: Any) -> Dict[str, Callable[[argparse.Namespace], None]]:
    """Build command handlers that use the injected context builder (no contest import)."""

    def _handle_train(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, data_schema, paths = _setup_handler_context(args, builder)
        validation_split = get_arg(args, 'validation_split', 0.2)
        train_data, val_data, _ = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
            validation_split=validation_split,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, data_schema, model_type)
        train_pipeline = TrainPipeline(
            config=config,
            train_data=train_data,
            val_data=val_data,
            **pipeline_kwargs,
        )
        results = train_pipeline.run()
        logger.info("Training complete: %s", results['success'])

    def _handle_test(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, _, paths = _setup_handler_context(args, builder)
        model_path = get_arg(args, 'model_path')
        if not model_path:
            raise ValueError("--model-path is required for test command")
        use_tta = getattr(args, 'use_tta', False)
        _, _, test_data = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, None, model_type)
        predict_pipeline = PredictPipeline(
            config=config,
            model_path=model_path,
            use_tta=use_tta,
            test_data=test_data,
            **pipeline_kwargs,
        )
        results = predict_pipeline.run()
        logger.info("Prediction complete: %s", results['success'])

    def _handle_train_test(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, data_schema, paths = _setup_handler_context(args, builder)
        use_tta = getattr(args, 'use_tta', False)
        validation_split = get_arg(args, 'validation_split', 0.2)
        train_data, val_data, test_data = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
            validation_split=validation_split,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, data_schema, model_type)
        workflow = TrainPredictWorkflow(
            config=config,
            use_tta=use_tta,
            train_data=train_data,
            val_data=val_data,
            test_data=test_data,
            **pipeline_kwargs,
        )
        results = workflow.run()
        logger.info("Train-test workflow complete: %s", results['success'])

    def _handle_grid_search(args: argparse.Namespace) -> None:
        _, config, model_type, _, _, _ = _setup_handler_context(args, builder)
        param_grid = {
            'learning_rate': [1e-3, 1e-4, 1e-5],
            'batch_size': [16, 32, 64],
        }
        grid_search = HyperparameterGridSearch(
            config=config,
            param_grid=param_grid,
            model_type=model_type,
        )
        results = grid_search.run()
        logger.info("Grid search complete: %s", results['success'])

    def _handle_cross_validate(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, data_schema, paths = _setup_handler_context(args, builder)
        n_folds = get_arg(args, 'n_folds', 5)
        train_data, _, _ = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
            n_folds=n_folds,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, data_schema, model_type)
        workflow = CrossValidateWorkflow(
            config=config,
            n_folds=n_folds,
            train_data=train_data,
            **pipeline_kwargs,
        )
        results = workflow.run()
        logger.info("Cross-validation complete: %s", results['success'])

    def _handle_ensemble(args: argparse.Namespace) -> None:
        model_paths_str = get_arg(args, 'model_paths')
        if not model_paths_str:
            raise ValueError("--model-paths is required for ensemble command")
        model_paths = parse_comma_separated(model_paths_str)
        if not model_paths:
            raise ValueError("--model-paths cannot be empty")
        predictions_list = []
        for model_path in model_paths:
            pred_path = Path(model_path) / 'predictions' / 'predictions.npy'
            if pred_path.exists():
                predictions_list.append(np.load(pred_path))
            else:
                logger.warning("Predictions not found for %s, skipping", model_path)
        if not predictions_list:
            raise ValueError("No valid predictions found")
        weights = None
        weights_str = get_arg(args, 'weights')
        if weights_str:
            weights = [float(w) for w in weights_str.split(',')]
            if len(weights) != len(predictions_list):
                raise ValueError(
                    f"Number of weights ({len(weights)}) must match number of models ({len(predictions_list)})"
                )
        ensemble_pred = simple_average(predictions_list, weights=weights)
        output_path = Path('output') / 'ensemble_predictions.npy'
        ensure_dir(output_path.parent)
        np.save(output_path, ensemble_pred)
        logger.info("Ensemble complete. Saved to %s", output_path)

    def _handle_export(args: argparse.Namespace) -> None:
        _, config, _, _, _, _ = _setup_handler_context(args, builder)
        model_path = get_arg(args, 'model_path')
        if not model_path:
            raise ValueError("--model-path is required for export command")
        export_dir = get_arg(args, 'export_dir', 'output/exports')
        export_pipeline = ExportPipeline(
            config=config,
            model_path=model_path,
            export_dir=export_dir,
        )
        results = export_pipeline.run()
        logger.info("Export complete: %s", results['success'])

    return {
        Command.TRAIN.value: _handle_train,
        Command.TEST.value: _handle_test,
        Command.TRAIN_TEST.value: _handle_train_test,
        Command.GRID_SEARCH.value: _handle_grid_search,
        Command.CROSS_VALIDATE.value: _handle_cross_validate,
        Command.ENSEMBLE.value: _handle_ensemble,
        Command.EXPORT_MODEL.value: _handle_export,
    }


def get_command_handlers(builder: Any) -> Dict[str, Callable[[argparse.Namespace], None]]:
    """
    Return framework command handlers that use the injected context builder.
    Call from scripts/run.py with builder from run_helpers.get_handler_context_builder(contest_name).
    """
    return _make_handlers(builder)
