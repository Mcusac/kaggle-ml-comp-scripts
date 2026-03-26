"""RNA3D notebook command builders.

Contest-specific glue for notebooks; shared ``run.py`` prefix comes from infra.
"""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1.notebook import build_run_py_base_command

_CONTEST = "rna3d"


def build_validate_data_command(
    data_root: Optional[str] = None,
    max_targets: int = 0,
    log_file: Optional[str] = None,
) -> List[str]:
    """Build command list for `run.py validate_data` for the RNA3D contest."""
    cmd = build_run_py_base_command(_CONTEST, "validate_data", data_root)
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    return cmd


def build_train_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    """Build command list for `run.py train` for the RNA3D contest."""
    if models is None:
        models = ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "train", data_root)
    cmd.extend(["--train-mode", str(train_mode), "--models", ",".join(models)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_tune_command(
    data_root: Optional[str] = None,
    model: str = "baseline_approx",
    search_type: str = "quick",
    max_targets: int = 0,
    log_file: Optional[str] = None,
) -> List[str]:
    """Build command list for `run.py tune` for the RNA3D contest."""
    cmd = build_run_py_base_command(_CONTEST, "tune", data_root)
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    return cmd


def build_submit_command(
    data_root: Optional[str] = None,
    strategy: str = "single",
    models: Optional[List[str]] = None,
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    log_file: Optional[str] = None,
) -> List[str]:
    """Build command list for `run.py submit` for the RNA3D contest."""
    if models is None:
        models = ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "submit", data_root)
    cmd.extend(["--strategy", str(strategy), "--models", ",".join(models)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(w) for w in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    return cmd
