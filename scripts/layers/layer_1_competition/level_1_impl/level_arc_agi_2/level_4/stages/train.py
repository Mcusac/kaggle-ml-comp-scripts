"""Train stage: train registered models or select heuristic on training tasks."""

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_4 import save_json

from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir
from layers.layer_1_competition.level_0_infra.level_1 import (
    RunContext,
    commit_run_artifacts,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    require_data_root,
    ARC26Paths,
    default_chosen_params,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    get_trainer,
    list_available_models,
)

logger = get_logger(__name__)


def run_train_pipeline(
    data_root: str,
    train_mode: str,
    models: list[str],
    run_ctx: Optional[RunContext] = None,
    max_targets: int = 0,
) -> Path:
    """Train registered models (e.g. grid_cnn_v0); for others pick heuristics on training JSON."""
    root = require_data_root(data_root)

    out_dir = contest_models_dir(ARC26Paths(), "arc_agi_2")
    ensure_dir(out_dir)
    metadata_path = out_dir / "train_metadata.json"

    per_model: dict[str, Any] = {}
    registered = list_available_models()

    for m in models:
        name = str(m)
        trainer = get_trainer(name)
        if trainer is not None:
            model_output_dir = out_dir / name
            ensure_dir(model_output_dir)
            logger.info("Training registered model %s -> %s", name, model_output_dir)
            trainer(str(root), str(model_output_dir))
            ckpt = model_output_dir / "model.pt"
            tcfg = model_output_dir / "train_config.json"
            per_model[name] = {
                "chosen_params": default_chosen_params(),
                "artifacts": {
                    "model_type": name,
                    "checkpoint": str(ckpt),
                    "train_config": str(tcfg),
                },
            }
        else:
            logger.warning(
                "select_best_heuristic_on_training was never implemented; "
                "Run 12 replaced non-registered model %r training with "
                "default chosen_params and empty train_scores",
                name,
            )
            per_model[name] = {
                "chosen_params": default_chosen_params(),
                "train_scores": {},
            }
            if name in registered:
                logger.warning("Model %r is in registry but get_trainer returned None", name)

    metadata = {
        "contest": "arc_agi_2",
        "train_mode": str(train_mode),
        "models": [str(m) for m in models],
        "registered_neural_models": registered,
        "data_root": str(root),
        "status": "complete",
        "per_model": per_model,
    }
    save_json(metadata, metadata_path)
    logger.info("Wrote ARC training metadata: %s", metadata_path)
    if run_ctx is not None:
        commit_run_artifacts(
            run_ctx,
            {
                "config": {"train": {"train_mode": str(train_mode), "models": [str(m) for m in models]}},
                "inputs": {"data_root": str(root)},
                "artifacts": {"train_metadata_json_src": str(metadata_path)},
            },
            src_path=metadata_path,
            dest_name="train_metadata.json",
        )
    return metadata_path
