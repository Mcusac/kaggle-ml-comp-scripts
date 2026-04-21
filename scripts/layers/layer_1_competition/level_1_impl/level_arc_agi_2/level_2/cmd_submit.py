"""``submit`` notebook command builder.

Shares argv primitives with ``level_1/cli/commands/build_submit_command.py`` via
``level_0_infra.level_0.argv_command_builders`` (extracted in Run 12).
"""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0.argv_command_builders import (
    append_run_args,
    append_strategy,
    append_tuned_config,
    resolve_and_append_models,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    append_llm,
    append_submit_args,
    base_cmd,
)

def build_submit_command(
    data_root: Optional[str] = None,
    strategy: str = "single",
    models: Optional[List[str]] = None,
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    tuned_config_path: Optional[str] = None,
    **llm_kwargs,
) -> List[str]:
    cmd = base_cmd("submit", data_root)
    append_strategy(cmd, strategy)
    resolve_and_append_models(cmd, models)
    append_submit_args(
        cmd,
        output_csv,
        max_targets,
        ensemble_weights,
        use_validation_for_stacking,
    )
    append_run_args(cmd, run_id, run_dir, log_file)
    append_tuned_config(cmd, tuned_config_path)
    append_llm(cmd, strategy=strategy, **llm_kwargs)
    return cmd
