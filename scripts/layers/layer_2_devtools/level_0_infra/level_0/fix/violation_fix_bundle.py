"""
Bundled file operations for RELATIVE_IN_LOGIC cleanup (general stack).

``scripts_dev_dir`` is the directory that contained the legacy ``_violation_fix_bundle``
script (typically ``.../scripts/dev``); relative patch paths are resolved under it.
"""

from pathlib import Path


def run_violation_fix_bundle(scripts_dev_dir: Path, dry_run: bool) -> None:
    sd = scripts_dev_dir.resolve()

    def rel_scripts(p: Path) -> Path:
        return p.relative_to(sd)

    def write_text(path: Path, text: str, dr: bool) -> None:
        action = "[DRY-RUN] write" if dr else "[APPLY] write"
        print(f"{action} {rel_scripts(path)}")
        if not dr:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def patch_text(path: Path, old: str, new: str, dr: bool) -> None:
        action = "[DRY-RUN] patch" if dr else "[APPLY] patch"
        print(f"{action} {rel_scripts(path)}")
        if not dr:
            t = path.read_text(encoding="utf-8")
            if old not in t:
                raise SystemExit(f"patch miss: {path}\nexpected:\n{old!r}")
            path.write_text(t.replace(old, new, 1), encoding="utf-8")

    def delete_file(path: Path, dr: bool) -> None:
        action = "[DRY-RUN] delete" if dr else "[APPLY] delete"
        print(f"{action} {rel_scripts(path)}")
        if not dr and path.is_file():
            path.unlink()

    pareto_src = sd / "level_0/grid_search/pareto_frontier.py"
    pareto_body = pareto_src.read_text(encoding="utf-8").replace(
        "from .result_selection import _filter_successful, _sentinel_value\n",
        "from level_0 import _filter_successful, _sentinel_value\n",
    )
    pareto_dest = sd / "level_1/grid_search/pareto_frontier.py"
    write_text(pareto_dest, pareto_body, dry_run)
    delete_file(pareto_src, dry_run)

    write_text(
        sd / "level_1/grid_search/__init__.py",
        '"""Pareto and grid helpers composed above level_0."""\n\n'
        "from .pareto_frontier import get_pareto_frontier\n\n"
        '__all__ = ["get_pareto_frontier"]\n',
        dry_run,
    )

    patch_text(
        sd / "level_0/grid_search/__init__.py",
        "from .pareto_frontier import get_pareto_frontier\n",
        "",
        dry_run,
    )
    patch_text(
        sd / "level_0/grid_search/__init__.py",
        "from .result_selection import filter_results, get_best_variant, get_top_n_variants\n",
        "from .result_selection import (\n"
        "    _filter_successful,\n"
        "    _sentinel_value,\n"
        "    filter_results,\n"
        "    get_best_variant,\n"
        "    get_top_n_variants,\n"
        ")\n",
        dry_run,
    )
    patch_text(
        sd / "level_0/grid_search/__init__.py",
        '    "get_pareto_frontier",\n',
        "",
        dry_run,
    )
    patch_text(
        sd / "level_0/grid_search/__init__.py",
        '    "resolve_varied_params",\n]',
        '    "resolve_varied_params",\n'
        '    "_filter_successful",\n'
        '    "_sentinel_value",\n]',
        dry_run,
    )

    patch_text(
        sd / "level_1/__init__.py",
        "from . import evaluation\n",
        "from . import evaluation\nfrom . import grid_search\n",
        dry_run,
    )
    patch_text(
        sd / "level_1/__init__.py",
        "from .evaluation import *\n",
        "from .evaluation import *\nfrom .grid_search import *\n",
        dry_run,
    )
    patch_text(
        sd / "level_1/__init__.py",
        "    + evaluation.__all__\n    + features.__all__\n",
        "    + evaluation.__all__\n    + grid_search.__all__\n    + features.__all__\n",
        dry_run,
    )

    ch_src = sd / "level_1/training/config_helper.py"
    ch_text = ch_src.read_text(encoding="utf-8")
    ch_text = ch_text.replace(
        "from level_0 import get_logger, get_config_value\n",
        "from level_0 import get_logger, get_config_value\nfrom level_1 import setup_mixed_precision\n",
    )
    ch_text = ch_text.replace(
        '''    @staticmethod
    def setup_mixed_precision(
        config: Union[Any, Dict[str, Any]],
        model_name: Optional[str],
        device: Any,
    ) -> tuple[bool, Optional[Any]]:
        """Set up mixed precision. Delegates to setup module."""
        from .setup import setup_mixed_precision as _setup
        return _setup(config, device)
''',
        '''    @staticmethod
    def setup_mixed_precision(
        config: Union[Any, Dict[str, Any]],
        model_name: Optional[str],
        device: Any,
    ) -> tuple[bool, Optional[Any]]:
        """Set up mixed precision. Delegates to level_1 setup."""
        return setup_mixed_precision(config, device)
''',
    )
    write_text(sd / "level_2/training/config_helper.py", ch_text, dry_run)
    delete_file(ch_src, dry_run)

    patch_text(
        sd / "level_1/training/__init__.py",
        "from .config_helper import (\n"
        "    ConfigHelper,\n"
        "    extract_config_settings,\n"
        "    get_required_config_value,\n"
        "    get_training_config_value,\n"
        ")\n",
        "",
        dry_run,
    )
    patch_text(
        sd / "level_1/training/__init__.py",
        '        "ConfigHelper",\n'
        '        "extract_config_settings",\n'
        '        "get_required_config_value",\n'
        '        "get_training_config_value",\n',
        "",
        dry_run,
    )

    l2t = sd / "level_2/training/__init__.py"
    patch_text(
        l2t,
        "from .multitask_config import MultiTaskTrainingConfig\n",
        "from .config_helper import (\n"
        "    ConfigHelper,\n"
        "    extract_config_settings,\n"
        "    get_required_config_value,\n"
        "    get_training_config_value,\n)\n"
        "from .multitask_config import MultiTaskTrainingConfig\n",
        dry_run,
    )
    patch_text(
        l2t,
        '    + [\n        "ModelCheckpointer",\n',
        '    + [\n'
        '        "ConfigHelper",\n'
        '        "extract_config_settings",\n'
        '        "get_required_config_value",\n'
        '        "get_training_config_value",\n'
        '        "ModelCheckpointer",\n',
        dry_run,
    )

    l2e = sd / "level_2/ensemble_strategies/__init__.py"
    patch_text(
        l2e,
        "from .handle_regression_ensemble_result import handle_regression_ensemble_result\n"
        "from .handle_stacking_results import handle_stacking_result, handle_hybrid_stacking_result\n"
        "from .pipeline_result_handler import handle_ensemble_result\n"
        "from .weight_matrix_builder import build_weight_matrix\n",
        "from .result_handler_common import log_pipeline_completion\n"
        "from .weight_matrix_builder import build_weight_matrix\n",
        dry_run,
    )
    patch_text(
        l2e,
        "    'merge_submissions',\n",
        "    'merge_submissions',\n    'log_pipeline_completion',\n",
        dry_run,
    )
    patch_text(
        l2e,
        "    'handle_regression_ensemble_result',\n"
        "    'handle_stacking_result',\n"
        "    'handle_hybrid_stacking_result',\n"
        "    'handle_ensemble_result',\n",
        "",
        dry_run,
    )

    for fn in (
        "handle_regression_ensemble_result.py",
        "handle_stacking_results.py",
        "pipeline_result_handler.py",
    ):
        src = sd / "level_2/ensemble_strategies" / fn
        dest = sd / "level_3/ensemble_strategies" / fn
        body = src.read_text(encoding="utf-8").replace(
            "from .result_handler_common import log_pipeline_completion\n",
            "from level_2 import log_pipeline_completion\n",
        )
        write_text(dest, body, dry_run)
        delete_file(src, dry_run)

    write_text(
        sd / "level_3/ensemble_strategies/__init__.py",
        '"""Ensemble result handlers composed above level_2."""\n\n'
        "from .handle_regression_ensemble_result import handle_regression_ensemble_result\n"
        "from .handle_stacking_results import handle_hybrid_stacking_result, handle_stacking_result\n"
        "from .pipeline_result_handler import handle_ensemble_result\n\n"
        "__all__ = [\n"
        '    "handle_regression_ensemble_result",\n'
        '    "handle_stacking_result",\n'
        '    "handle_hybrid_stacking_result",\n'
        '    "handle_ensemble_result",\n'
        "]\n",
        dry_run,
    )

    init_l3 = sd / "level_3/__init__.py"
    patch_text(
        init_l3,
        "from . import dataloader\n",
        "from . import dataloader\nfrom . import ensemble_strategies\n",
        dry_run,
    )
    patch_text(
        init_l3,
        "from .dataloader import *\n",
        "from .dataloader import *\nfrom .ensemble_strategies import *\n",
        dry_run,
    )
    patch_text(
        init_l3,
        "__all__ = (\n    dataloader.__all__\n",
        "__all__ = (\n    dataloader.__all__\n    + ensemble_strategies.__all__\n",
        dry_run,
    )

    for fn in ("cross_validate.py", "train_and_export.py"):
        src = sd / "level_8/training" / fn
        dest = sd / "level_9/training" / fn
        body = src.read_text(encoding="utf-8").replace(
            "from .train_pipeline import TrainPipeline\n",
            "from level_8 import TrainPipeline\n",
        )
        write_text(dest, body, dry_run)
        delete_file(src, dry_run)

    write_text(
        sd / "level_9/training/__init__.py",
        '"""Training workflows composed above level_8."""\n\n'
        "from .cross_validate import CrossValidateWorkflow\n"
        "from .train_and_export import TrainAndExportWorkflow\n\n"
        '__all__ = ["CrossValidateWorkflow", "TrainAndExportWorkflow"]\n',
        dry_run,
    )

    patch_text(
        sd / "level_8/training/__init__.py",
        "from .cross_validate import CrossValidateWorkflow\n",
        "",
        dry_run,
    )
    patch_text(
        sd / "level_8/training/__init__.py",
        "from .train_and_export import TrainAndExportWorkflow\n",
        "",
        dry_run,
    )
    patch_text(
        sd / "level_8/training/__init__.py",
        '    "CrossValidateWorkflow",\n',
        "",
        dry_run,
    )
    patch_text(
        sd / "level_8/training/__init__.py",
        '    "TrainAndExportWorkflow",\n',
        "",
        dry_run,
    )

    patch_text(
        sd / "level_8/__init__.py",
        "from .training import (\n    CrossValidateWorkflow,\n    TrainAndExportWorkflow,\n    TrainPipeline,\n",
        "from .training import (\n    TrainPipeline,\n",
        dry_run,
    )
    patch_text(
        sd / "level_8/__init__.py",
        '    "CrossValidateWorkflow",\n',
        "",
        dry_run,
    )
    patch_text(
        sd / "level_8/__init__.py",
        '    "TrainAndExportWorkflow",\n',
        "",
        dry_run,
    )

    write_text(
        sd / "level_9/__init__.py",
        '"""Level 9: Hyperparameter grid search, train-then-predict workflow."""\n\n'
        "from .training import CrossValidateWorkflow, TrainAndExportWorkflow\n"
        "from .grid_search import (\n"
        "    HyperparameterGridSearch,\n"
        "    RegressionGridSearch,\n"
        "    attach_paths_to_config,\n"
        "    dataset_grid_search_pipeline,\n"
        "    regression_grid_search_pipeline,\n"
        "    test_max_augmentation_pipeline,\n"
        ")\n"
        "from .train_predict import TrainPredictWorkflow\n\n"
        "__all__ = [\n"
        '    "CrossValidateWorkflow",\n'
        '    "TrainAndExportWorkflow",\n'
        '    "attach_paths_to_config",\n'
        '    "dataset_grid_search_pipeline",\n'
        '    "HyperparameterGridSearch",\n'
        '    "RegressionGridSearch",\n'
        '    "regression_grid_search_pipeline",\n'
        '    "test_max_augmentation_pipeline",\n'
        '    "TrainPredictWorkflow",\n'
        "]\n",
        dry_run,
    )

    patch_text(
        sd / "layers/layer_1_competition/level_0_infra/level_1/handlers/command_handlers.py",
        "from level_8 import TrainPipeline, CrossValidateWorkflow\n",
        "from level_8 import TrainPipeline\nfrom level_9 import CrossValidateWorkflow\n",
        dry_run,
    )

    patch_text(
        sd / "layers/layer_1_competition/level_0_infra/level_0/feature_extraction.py",
        "from level_1.training.config_helper import get_required_config_value\n",
        "from level_2.training.config_helper import get_required_config_value\n",
        dry_run,
    )

    patch_text(
        sd / "layers/layer_1_competition/level_1_impl/level_csiro/level_0/config_helper.py",
        "from level_1 import ConfigHelper\n",
        "from level_2 import ConfigHelper\n",
        dry_run,
    )

    patch_text(
        sd / "level_5/training/base_model_trainer.py",
        "from level_1 import (\n"
        "    get_device,\n"
        "    extract_config_settings,\n"
        "    get_training_config_value,\n"
        "    setup_mixed_precision,\n)\n",
        "from level_1 import get_device, setup_mixed_precision\n"
        "from level_2 import extract_config_settings, get_training_config_value\n",
        dry_run,
    )
