"""``train_and_submit`` notebook command builder."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0 import (
    append_run_args,
    append_strategy,
    append_train_mode,
    resolve_and_append_models,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    append_llm,
    append_submit_args,
    base_cmd,
)

def build_train_and_submit_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    strategy: str = "single",
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    **llm_kwargs,
) -> List[str]:
    cmd = base_cmd("train_and_submit", data_root)
    append_train_mode(cmd, train_mode)
    resolve_and_append_models(cmd, models)
    append_strategy(cmd, strategy)
    append_submit_args(
        cmd,
        output_csv,
        max_targets,
        ensemble_weights,
        use_validation_for_stacking,
    )
    append_run_args(cmd, run_id, run_dir, log_file)
    append_llm(cmd, strategy=strategy, **llm_kwargs)
    return cmd
