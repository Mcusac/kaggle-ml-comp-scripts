"""Tune stage: select best heuristic and optionally score neural on evaluation."""

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_4 import save_json

from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    read_submit_max_tasks_env,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    default_chosen_params,
    get_per_model_entry,
    resolve_neural_paths_from_entry,
    ARC26Paths,
    require_data_root,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    RunContext,
    commit_run_artifacts,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    score_neural_on_evaluation,
)



logger = get_logger(__name__)


def run_tune_pipeline(
    data_root: str,
    model_name: str,
    search_type: str = "quick",
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
    train_metadata_json: Optional[str] = None,
) -> Path:
    """Select best baseline heuristic using evaluation tasks when solutions exist."""
    root = require_data_root(data_root)

    out_dir = contest_models_dir(ARC26Paths(), "arc_agi_2") / str(model_name)
    ensure_dir(out_dir)
    tune_path = out_dir / "best_config.json"
    logger.warning(
        "select_best_heuristic was never implemented; Run 12 replaced the "
        "tune selection with default chosen_params and empty tune_scores"
    )
    chosen_params = default_chosen_params()
    tune_scores: dict[str, float] = {}
    metadata_hint = train_metadata_json
    if not metadata_hint:
        candidate = contest_models_dir(ARC26Paths(), "arc_agi_2") / "train_metadata.json"
        if candidate.is_file():
            metadata_hint = str(candidate)

    neural_eval_exact_match: float | None = None
    entry = get_per_model_entry(metadata_hint, str(model_name))
    ckpt_path, cfg_path = resolve_neural_paths_from_entry(entry)
    if ckpt_path is not None and cfg_path is not None:
        neural_eval_exact_match = score_neural_on_evaluation(
            str(root),
            str(ckpt_path),
            str(cfg_path),
            max_tasks=read_submit_max_tasks_env() or 0,
            max_targets=int(max_targets or 0),
        )

    result = {
        "model_name": str(model_name),
        "search_type": str(search_type),
        "max_targets": int(max_targets),
        "chosen_params": chosen_params,
        "tune_scores": tune_scores,
    }
    if neural_eval_exact_match is not None:
        result["neural_eval_exact_match"] = float(neural_eval_exact_match)
    save_json(result, tune_path)
    logger.info("Wrote ARC tuning metadata: %s (chosen=%s)", tune_path, chosen_params)
    if run_ctx is not None:
        commit_run_artifacts(
            run_ctx,
            {
                "config": {
                    "tune": {
                        "model_name": str(model_name),
                        "search_type": str(search_type),
                        "max_targets": int(max_targets),
                    }
                },
                "inputs": {"data_root": str(root)},
                "artifacts": {"best_config_json_src": str(tune_path)},
                "metrics": {"tune_scores": tune_scores},
            },
            src_path=tune_path,
            dest_name="best_config.json",
        )
    return tune_path
