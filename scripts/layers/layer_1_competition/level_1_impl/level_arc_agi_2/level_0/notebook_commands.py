"""ARC notebook command builders."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

_CONTEST = "arc_agi_2"


def build_validate_data_command(
    data_root: Optional[str] = None,
    max_targets: int = 0,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = build_run_py_base_command(_CONTEST, "validate_data", data_root)
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_train_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "train", data_root)
    cmd.extend(["--train-mode", str(train_mode), "--models", ",".join(model_names)])
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_tune_command(
    data_root: Optional[str] = None,
    model: str = "baseline_approx",
    search_type: str = "quick",
    max_targets: int = 0,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = build_run_py_base_command(_CONTEST, "tune", data_root)
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


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
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "submit", data_root)
    cmd.extend(["--strategy", str(strategy), "--models", ",".join(model_names)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    if tuned_config_path:
        cmd.extend(["--tuned-config", str(tuned_config_path)])
    return cmd


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
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "train_and_submit", data_root)
    cmd.extend(["--train-mode", str(train_mode), "--models", ",".join(model_names)])
    cmd.extend(["--strategy", str(strategy)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def build_tune_and_submit_command(
    data_root: Optional[str] = None,
    model: str = "baseline_approx",
    search_type: str = "quick",
    strategy: str = "single",
    models: Optional[List[str]] = None,
    output_csv: Optional[str] = None,
    max_targets: int = 0,
    ensemble_weights: Optional[List[float]] = None,
    use_validation_for_stacking: bool = True,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(_CONTEST, "tune_and_submit", data_root)
    cmd.extend(["--model", str(model), "--search-type", str(search_type)])
    cmd.extend(["--strategy", str(strategy), "--models", ",".join(model_names)])
    if output_csv:
        cmd.extend(["--output-csv", str(output_csv)])
    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])
    if ensemble_weights:
        cmd.extend(["--ensemble-weights", ",".join(str(v) for v in ensemble_weights)])
    if not use_validation_for_stacking:
        cmd.append("--no-validation-stacking")
    if run_id:
        cmd.extend(["--run-id", str(run_id)])
    if run_dir:
        cmd.extend(["--run-dir", str(run_dir)])
    if log_file:
        cmd.extend(["--log-file", str(log_file)])
    return cmd

